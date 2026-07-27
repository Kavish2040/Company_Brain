/**
 * Live-collaboration client.
 *
 * The principal travels in the WebSocket subprotocol, not a query parameter and
 * not a message field. A browser can't set `X-Principal` on a socket, and the
 * subprotocol is the closest equivalent: fixed at connect time, impossible to
 * restate per message. Same demo stand-in as the header, same shape.
 *
 * Server-authoritative, last-write-wins. The server owns `body`; this client
 * sends edits and applies whatever comes back — except the echo of its own
 * in-flight edit, which would otherwise yank the caret mid-keystroke.
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type Participant = {
  connection: string;
  principal: string;
  display: string;
  /** A palette *name* — see CARET_CLASS. The server never sends hex. */
  color: string;
  anchor: number;
  head: number;
};

export type CollabStatus = "idle" | "connecting" | "live" | "denied" | "closed";

/** Close codes the server uses. Neither is worth retrying. */
const CLOSE_BAD_IDENTITY = 4401;
const CLOSE_NOT_VISIBLE = 4404;

const SUBPROTOCOL = "cb.principal.";

function socketUrl(path: string): string {
  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${scheme}//${window.location.host}${path}`;
}

export type Collab = {
  status: CollabStatus;
  body: string;
  revision: number;
  participants: Participant[];
  /** Set when the server refused an edit — currently only fence tampering. */
  rejected: string | null;
  /** Our own connection id, so remote carets can exclude us. */
  connection: string | null;
  edit: (body: string) => void;
  moveCursor: (anchor: number, head: number) => void;
};

export function useCollab(
  nodeId: string | null,
  principal: string,
  enabled: boolean,
): Collab {
  const [status, setStatus] = useState<CollabStatus>("idle");
  const [body, setBody] = useState("");
  const [revision, setRevision] = useState(0);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [rejected, setRejected] = useState<string | null>(null);
  const [connection, setConnection] = useState<string | null>(null);

  const socket = useRef<WebSocket | null>(null);
  const me = useRef<string | null>(null);
  const revisionRef = useRef(0);
  // Set while our own edit is in flight so we can ignore its echo.
  const pending = useRef(false);

  useEffect(() => {
    if (!enabled || !nodeId) {
      setStatus("idle");
      return;
    }

    let closed = false;
    let retry: number | undefined;
    let attempt = 0;

    const open = () => {
      if (closed) return;
      setStatus("connecting");
      const ws = new WebSocket(
        socketUrl(`/api/collab/node/${nodeId}`),
        [`${SUBPROTOCOL}${principal}`],
      );
      socket.current = ws;

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        switch (message.type) {
          case "welcome":
            me.current = message.connection;
            setConnection(message.connection);
            setBody(message.body);
            setRevision(message.revision);
            revisionRef.current = message.revision;
            setParticipants(message.participants ?? []);
            setStatus("live");
            attempt = 0;
            break;
          case "sync":
            setRevision(message.revision);
            revisionRef.current = message.revision;
            // Our own echo would reset the textarea and move the caret.
            if (message.by === me.current) {
              pending.current = false;
            } else {
              setBody(message.body);
            }
            break;
          case "presence":
            setParticipants(message.participants ?? []);
            break;
          case "rejected":
            // The server refused the write and sent authoritative text back.
            setRejected(message.reason);
            setBody(message.body);
            setRevision(message.revision);
            revisionRef.current = message.revision;
            pending.current = false;
            break;
        }
      };

      ws.onclose = (event) => {
        socket.current = null;
        if (closed) return;
        if (event.code === CLOSE_BAD_IDENTITY || event.code === CLOSE_NOT_VISIBLE) {
          setStatus("denied");
          return; // refusals are answers, not failures to retry
        }
        setStatus("closed");
        attempt += 1;
        retry = window.setTimeout(open, Math.min(1000 * 2 ** attempt, 8000));
      };
    };

    open();
    return () => {
      closed = true;
      if (retry) window.clearTimeout(retry);
      socket.current?.close();
      socket.current = null;
      me.current = null;
      setParticipants([]);
      setRejected(null);
    };
  }, [nodeId, principal, enabled]);

  const edit = useCallback((next: string) => {
    setBody(next); // optimistic: typing must not wait on a round trip
    setRejected(null);
    const ws = socket.current;
    if (ws?.readyState !== WebSocket.OPEN) return;
    pending.current = true;
    ws.send(
      JSON.stringify({ type: "edit", base_revision: revisionRef.current, body: next }),
    );
  }, []);

  const moveCursor = useCallback((anchor: number, head: number) => {
    const ws = socket.current;
    if (ws?.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "cursor", anchor, head }));
  }, []);

  return { status, body, revision, participants, rejected, connection, edit, moveCursor };
}
