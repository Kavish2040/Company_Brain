"""Composition root.

One place where providers are chosen, so every entry point (CLI, MCP, API) gets
the same wiring and the offline/online decision is made exactly once.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from company_brain.acl.grants import AccessFilter, GrantTable, elevate
from company_brain.corpus.generate import CHANNELS
from company_brain.extract.base import CachedExtractor, Extractor
from company_brain.extract.rules import Roster
from company_brain.index.base import Embedder, HashingEmbedder, IndexedNode
from company_brain.index.memory import MemoryIndex
from company_brain.normalize.base import Registry
from company_brain.normalize.formats import default_registry
from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity
from company_brain.store.backend import LocalFsBackend
from company_brain.store.repository import Repository
from company_brain.synthesize.answer import Synthesizer

STORE_ROOT = Path("store")
CORPUS_ROOT = Path("corpus/synthetic")

# Synthetic principals for M1. M2 replaces these with directory-synced grants.
PRINCIPALS: dict[str, Principal] = {
    "ceo": Principal(id="ceo", kind=PrincipalKind.USER, display="Chief Executive"),
    "support-lead": Principal(
        id="support-lead", kind=PrincipalKind.USER, display="Dev Oyelaran"
    ),
    "eng-ic": Principal(id="eng-ic", kind=PrincipalKind.USER, display="Sam Kelly"),
    "contractor": Principal(
        id="contractor", kind=PrincipalKind.USER, display="External Contractor"
    ),
}


def build_grants() -> GrantTable:
    """Grants for the synthetic principals.

    Only the CEO holds the restricted `leadership-comp` channel. That single
    asymmetry is what the acceptance suite's leak test turns on.
    """
    grants = GrantTable()
    docs = ("fs:corpus:docs", Sensitivity.INTERNAL)
    mail = ("gmail:mailbox:meridian", Sensitivity.INTERNAL)

    def channel(name: str) -> tuple[str, Sensitivity]:
        cid, _, tier = next(c for c in CHANNELS if c[1] == name)
        return f"slack:channel:{cid}", Sensitivity(tier)

    plan: dict[str, list[tuple[str, Sensitivity]]] = {
        "ceo": [
            docs,
            mail,
            channel("general"),
            channel("engineering"),
            channel("support"),
            channel("finance"),
            channel("leadership-comp"),
        ],
        "support-lead": [
            docs,
            mail,
            channel("general"),
            channel("support"),
            channel("engineering"),
        ],
        "eng-ic": [docs, mail, channel("general"), channel("engineering")],
        "contractor": [channel("general")],
    }
    for principal_id, entries in plan.items():
        for ref, tier in entries:
            grants.grant(principal_id, ref, tier)
    return grants


@dataclass(slots=True)
class Providers:
    extractor: Extractor
    embedder: Embedder
    synthesizer_name: str
    offline: bool
    reason: str

    def synthesizer(self) -> Synthesizer:
        from company_brain.synthesize.answer import ExtractiveSynthesizer

        if self.offline:
            return ExtractiveSynthesizer()
        from company_brain.synthesize.claude import ClaudeSynthesizer

        return ClaudeSynthesizer()


def _offline_requested() -> bool:
    return os.environ.get("COMPANY_BRAIN_OFFLINE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def choose_providers(roster: Roster) -> Providers:
    """Pick real or offline providers from what credentials exist.

    Both keys or neither. A half-configured run — Claude extraction scored
    against hash-based embeddings — is a hybrid nobody asked for, and "offline,
    because OPENAI_API_KEY is unset" is a far easier failure to diagnose than
    unexplained retrieval quality.

    Always reports *why*, so a run is never silently degraded.
    """
    from company_brain.extract.rules import RuleBasedExtractor

    fallback = RuleBasedExtractor(roster)

    if _offline_requested():
        return Providers(
            extractor=fallback,
            embedder=HashingEmbedder(),
            synthesizer_name="extractive-offline",
            offline=True,
            reason="offline providers (COMPANY_BRAIN_OFFLINE is set)",
        )

    missing = [
        name for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY") if not os.environ.get(name)
    ]
    if missing:
        return Providers(
            extractor=fallback,
            embedder=HashingEmbedder(),
            synthesizer_name="extractive-offline",
            offline=True,
            reason=f"offline providers ({', '.join(missing)} not set)",
        )

    from company_brain.extract.claude import ClaudeExtractor
    from company_brain.index.openai_embed import OpenAIEmbedder

    extractor = ClaudeExtractor(roster)
    embedder = OpenAIEmbedder()
    return Providers(
        extractor=extractor,
        embedder=embedder,
        synthesizer_name="claude",
        offline=False,
        reason=(
            f"online: extract={extractor.model}, synth=claude-opus-5, embed={embedder.name}"
        ),
    )


@dataclass(slots=True)
class App:
    repo: Repository
    registry: Registry
    grants: GrantTable
    index: MemoryIndex
    providers: Providers

    def principal(self, name: str) -> Principal:
        try:
            return PRINCIPALS[name]
        except KeyError:
            raise SystemExit(
                f"unknown principal {name!r}; try one of {', '.join(sorted(PRINCIPALS))}"
            ) from None

    def access(self, principal: Principal) -> AccessFilter:
        return AccessFilter(self.grants, principal)

    def load_index(self) -> int:
        """Rebuild the index from markdown. This *is* invariant 2."""
        payload: list[tuple[IndexedNode, str]] = []
        for node in self.repo.walk():
            fm = node.frontmatter
            payload.append(
                (
                    IndexedNode(
                        id=fm.id,
                        type=str(fm.type),
                        title=fm.title,
                        acl_ref=fm.acl.ref,
                        sensitivity=fm.acl.sensitivity,
                        status=str(fm.status),
                        content_sha256=fm.source.content_sha256 if fm.source else "",
                        edges=fm.relations,
                    ),
                    node.body,
                )
            )
        return self.index.rebuild(payload)


def build_app(store_root: Path = STORE_ROOT, *, frozen: bool = False) -> App:
    from company_brain.connectors.local_fs import build_roster

    backend = LocalFsBackend(store_root)
    repo = Repository(backend)
    providers = choose_providers(build_roster())
    return App(
        repo=repo,
        registry=default_registry(),
        grants=build_grants(),
        index=MemoryIndex(providers.embedder),
        providers=providers,
    )


def cached_extractor(app: App, store_root: Path, *, frozen: bool) -> CachedExtractor:
    return CachedExtractor(app.providers.extractor, LocalFsBackend(store_root), frozen=frozen)


__all__ = [
    "CORPUS_ROOT",
    "PRINCIPALS",
    "STORE_ROOT",
    "App",
    "build_app",
    "build_grants",
    "cached_extractor",
    "elevate",
]
