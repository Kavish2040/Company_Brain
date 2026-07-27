"""Shared acceptance fixtures.

`test_m1.py` and `test_m3_resolve.py` each build their own store, because each
mutates it. The M4 evaluation harness only reads, so it gets a session-scoped
corpus + store here rather than paying for a third ingest.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from company_brain.app import App, build_app, cached_extractor
from company_brain.connectors.local_fs import LocalIngest
from company_brain.corpus.generate import generate


@pytest.fixture(scope="session")
def ingested(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """A generated corpus, ingested once, read-only from here on."""
    base = tmp_path_factory.mktemp("m4")
    corpus, store = base / "corpus", base / "store"
    generate(corpus)

    app = build_app(store)
    report = LocalIngest(
        app.repo, app.registry, cached_extractor(app, store, frozen=False)
    ).run(corpus)
    assert not report.skipped, report.skipped[:3]
    return corpus, store


@pytest.fixture(scope="session")
def indexed_app(ingested: tuple[Path, Path]) -> App:
    _, store = ingested
    app = build_app(store)
    app.load_index()
    return app
