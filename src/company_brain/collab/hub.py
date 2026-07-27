"""Async transport for live rooms: fan-out and debounced persistence.

Split from `session.py` on purpose. The merge rule is synchronous and testable
without a socket; everything that needs an event loop is here.

The debounce is the "no save button": edits land in memory immediately and hit
the markdown store once the typing stops. A crash inside that window loses the
last few hundred milliseconds, which is the price of not writing a file per
keystroke and is acceptable for a demo surface. It would not be acceptable for
the canonical store of record without a write-ahead log.
"""

from __future__ import annotations

import asyncio
import itertools
from typing import Any, Protocol

from company_brain.collab.session import RoomState, SessionRegistry

FLUSH_DEBOUNCE_SECONDS = 0.8


class Sink(Protocol):
    """The half of `WebSocket` this module uses.

    Narrow on purpose: it keeps `hub` importable without FastAPI and lets tests
    drive fan-out with a list.
    """

    async def send_json(self, data: Any) -> None: ...


class CollabHub:
    """Connections, broadcast, and the flush timer for every open room."""

    def __init__(
        self, registry: SessionRegistry, *, debounce: float = FLUSH_DEBOUNCE_SECONDS
    ) -> None:
        self.registry = registry
        self.debounce = debounce
        self._sinks: dict[str, dict[str, Sink]] = {}
        self._flushes: dict[str, asyncio.Task[None]] = {}
        # room -> connection -> principal id. `RoomState` already tracks this for
        # node rooms; the shared ask room has no RoomState, and keeping the map
        # on the hub beats a module-level global that outlives a test.
        self._members: dict[str, dict[str, str]] = {}
        # A counter, not uuid4: connection ids are compared and sorted (presence
        # ordering) and never reach the store, so monotonic beats random.
        self._ids = itertools.count(1)

    def next_connection_id(self) -> str:
        return f"c{next(self._ids)}"

    # ---- membership ----------------------------------------------------

    def attach(self, node_id: str, connection: str, sink: Sink, principal: str = "") -> None:
        self._sinks.setdefault(node_id, {})[connection] = sink
        if principal:
            self._members.setdefault(node_id, {})[connection] = principal

    def detach(self, node_id: str, connection: str) -> None:
        sinks = self._sinks.get(node_id)
        if sinks is not None:
            sinks.pop(connection, None)
            if not sinks:
                del self._sinks[node_id]
        members = self._members.get(node_id)
        if members is not None:
            members.pop(connection, None)
            if not members:
                del self._members[node_id]

    def members(self, node_id: str) -> dict[str, str]:
        """connection -> principal, in stable connection order."""
        return dict(sorted(self._members.get(node_id, {}).items()))

    def audience(self, node_id: str) -> int:
        return len(self._sinks.get(node_id, {}))

    def sink(self, node_id: str, connection: str) -> Sink | None:
        return self._sinks.get(node_id, {}).get(connection)

    async def send_to(self, node_id: str, connection: str, message: dict[str, Any]) -> None:
        """Send to one connection. Used where each recipient gets *different*
        content — the shared ask room answers every principal separately."""
        sink = self.sink(node_id, connection)
        if sink is None:
            return
        try:
            await sink.send_json(message)
        except Exception:  # already gone; the disconnect handler will tidy up
            self.detach(node_id, connection)

    # ---- fan-out -------------------------------------------------------

    async def broadcast(
        self, node_id: str, message: dict[str, Any], *, exclude: str | None = None
    ) -> None:
        """Send to everyone in a room, tolerating dead sockets.

        A send that fails is a client that has already gone away; the disconnect
        handler will clean it up. Letting the exception escape here would abort
        the fan-out and leave the rest of the room stale.
        """
        targets = [
            (conn, sink)
            for conn, sink in self._sinks.get(node_id, {}).items()
            if conn != exclude
        ]
        for conn, sink in targets:
            try:
                await sink.send_json(message)
            except Exception:  # a dead socket must not stop the fan-out
                self.detach(node_id, conn)

    async def announce_presence(self, room: RoomState) -> None:
        await self.broadcast(
            room.node_id, {"type": "presence", "participants": room.presence()}
        )

    # ---- persistence ---------------------------------------------------

    def schedule_flush(self, node_id: str) -> None:
        """(Re)start the quiet-period timer for a room."""
        existing = self._flushes.get(node_id)
        if existing is not None:
            existing.cancel()
        self._flushes[node_id] = asyncio.create_task(self._flush_after_quiet(node_id))

    async def _flush_after_quiet(self, node_id: str) -> None:
        try:
            await asyncio.sleep(self.debounce)
        except asyncio.CancelledError:
            return  # superseded by a newer keystroke
        await self.flush_now(node_id)

    async def flush_now(self, node_id: str) -> bool:
        """Persist immediately. Called by the timer and on the last disconnect.

        `Repository.put` is blocking file IO, so it runs off the loop — a
        broadcast to the rest of the room should not wait on fsync.
        """
        wrote = await asyncio.to_thread(self.registry.persist, node_id)
        if wrote:
            room = self.registry.find(node_id)
            revision = room.revision if room else 0
            await self.broadcast(node_id, {"type": "saved", "revision": revision})
        return wrote

    async def shutdown_room(self, node_id: str) -> bool:
        """Flush and drop a room once its last editor leaves.

        Returns True if the store changed, so the caller can decide whether the
        derived index needs rebuilding. Deliberately *not* done per keystroke:
        rebuilding a 232-node index on every character is the kind of thing that
        makes a demo feel broken.
        """
        pending = self._flushes.pop(node_id, None)
        if pending is not None:
            pending.cancel()
        wrote = await self.flush_now(node_id)
        self.registry.close_if_empty(node_id)
        return wrote
