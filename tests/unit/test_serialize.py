"""Determinism and round-trip tests for the canonical serializer.

These guard invariant 3. If any of them fail, the M1 acceptance criterion
(byte-identical re-ingestion) is not achievable.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from company_brain.schemas.acl import AclRef, Sensitivity, narrowest
from company_brain.schemas.edges import (
    Edge,
    EdgeStatus,
    Evidence,
    Predicate,
    Provenance,
    decide_status,
)
from company_brain.schemas.ids import document_slug, make_id, slugify, split_id
from company_brain.schemas.nodes import (
    ExtractionRef,
    ExtractionStatus,
    Frontmatter,
    Node,
    NodeType,
    NormalizerRef,
    SourceRef,
    Timestamps,
)
from company_brain.store.serialize import dump_node, parse_node

SHA = "a" * 64


def make_document() -> Node:
    return Node(
        frontmatter=Frontmatter(
            id="documents/slack/eng-standup-2024-03-14-a91f3c",
            type=NodeType.DOCUMENT,
            title="Eng standup — 2024-03-14",
            acl=AclRef(ref="slack:channel:C0ENG", sensitivity=Sensitivity.INTERNAL),
            source=SourceRef(
                connector="slack",
                uri="slack://T01ABC/C0ENG/p1710403200000100",
                external_id="1710403200.000100",
                external_version="1710403200.000100",
                content_sha256=SHA,
            ),
            authors=("people/sam-kaur",),
            timestamps=Timestamps(
                created=datetime(2024, 3, 14, 9, 0, tzinfo=UTC),
                modified=datetime(2024, 3, 14, 9, 31, tzinfo=UTC),
            ),
            normalizer=NormalizerRef(name="slack_export", version="1.0.0"),
            extraction=ExtractionRef(
                model="claude-sonnet-5",
                prompt_version="entity-v3",
                cache_key="b7c1e0",
                status=ExtractionStatus.ACCEPTED,
            ),
            relations=(
                Edge(
                    predicate=Predicate.MENTIONS,
                    object="tools/netsuite",
                    confidence=0.94,
                    provenance=Provenance.LLM,
                    status=EdgeStatus.ACCEPTED,
                    evidence=(Evidence(node="self", span=(412, 431)),),
                ),
                Edge(
                    predicate=Predicate.AUTHORED_BY,
                    object="people/sam-kaur",
                    confidence=1.0,
                    provenance=Provenance.STRUCTURAL,
                    status=EdgeStatus.ACCEPTED,
                ),
            ),
        ),
        body="Sam raised that the [[tools/netsuite|NetSuite]] renewal lands in April.",
    )


class TestRoundTrip:
    def test_dump_parse_dump_is_stable(self) -> None:
        once = dump_node(make_document())
        assert dump_node(parse_node(once)) == once

    def test_parsed_model_equals_original(self) -> None:
        node = make_document()
        assert parse_node(dump_node(node)) == node

    def test_repeated_dumps_are_identical(self) -> None:
        # Catches dict/set iteration order leaking into output.
        outputs = {dump_node(make_document()) for _ in range(25)}
        assert len(outputs) == 1


class TestCanonicalForm:
    def test_ends_with_exactly_one_newline(self) -> None:
        text = dump_node(make_document())
        assert text.endswith("\n")
        assert not text.endswith("\n\n")

    def test_no_trailing_whitespace_on_any_line(self) -> None:
        for line in dump_node(make_document()).split("\n"):
            assert line == line.rstrip(), f"trailing whitespace: {line!r}"

    def test_no_crlf(self) -> None:
        assert "\r" not in dump_node(make_document())

    def test_declared_key_order_is_respected(self) -> None:
        text = dump_node(make_document())
        assert text.index("\nid:") < text.index("\ntitle:") < text.index("\nrelations:")

    def test_relations_sorted_regardless_of_input_order(self) -> None:
        node = make_document()
        flipped = node.frontmatter.model_copy(
            update={"relations": tuple(reversed(node.frontmatter.relations))}
        )
        assert dump_node(Node(frontmatter=flipped, body=node.body)) == dump_node(node)

    def test_body_crlf_and_trailing_space_normalized(self) -> None:
        node = make_document()
        messy = Node(frontmatter=node.frontmatter, body="line one   \r\nline two\t\r\n\n\n")
        assert "line one\nline two" in dump_node(messy)
        assert "   \n" not in dump_node(messy)


class TestTimestamps:
    def test_equal_instants_in_different_zones_emit_identically(self) -> None:
        node = make_document()
        utc = datetime(2024, 3, 14, 9, 0, tzinfo=UTC)
        ist = utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
        a = node.frontmatter.model_copy(update={"timestamps": Timestamps(created=utc)})
        b = node.frontmatter.model_copy(update={"timestamps": Timestamps(created=ist)})
        assert dump_node(Node(frontmatter=a)) == dump_node(Node(frontmatter=b))

    def test_naive_datetime_rejected(self) -> None:
        with pytest.raises(ValueError, match="timezone-aware"):
            Timestamps(created=datetime(2024, 3, 14, 9, 0))

    def test_modified_before_created_rejected(self) -> None:
        with pytest.raises(ValueError, match="precedes"):
            Timestamps(
                created=datetime(2024, 3, 14, 9, 0, tzinfo=UTC),
                modified=datetime(2024, 3, 13, 9, 0, tzinfo=UTC),
            )


class TestFrontmatterValidation:
    def test_id_type_mismatch_rejected(self) -> None:
        with pytest.raises(ValueError, match="implies type"):
            Frontmatter(
                id="people/sam-kaur",
                type=NodeType.DOCUMENT,
                title="x",
                acl=AclRef(ref="fs:corpus:public", sensitivity=Sensitivity.PUBLIC),
            )

    def test_document_without_source_rejected(self) -> None:
        with pytest.raises(ValueError, match="no source block"):
            Frontmatter(
                id="documents/x-abc123",
                type=NodeType.DOCUMENT,
                title="x",
                acl=AclRef(ref="fs:corpus:public", sensitivity=Sensitivity.PUBLIC),
            )

    def test_self_edge_rejected(self) -> None:
        with pytest.raises(ValueError, match="self-edge"):
            Frontmatter(
                id="people/sam-kaur",
                type=NodeType.PERSON,
                title="Sam Kaur",
                acl=AclRef(ref="fs:corpus:public", sensitivity=Sensitivity.PUBLIC),
                relations=(
                    Edge(
                        predicate=Predicate.SAME_AS,
                        object="people/sam-kaur",
                        confidence=1.0,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ),
                ),
            )

    def test_duplicate_relations_rejected(self) -> None:
        # Would violate edges' (subject, predicate, object) primary key at index
        # time, long after the file was written.
        with pytest.raises(ValueError, match="duplicate relations"):
            Frontmatter(
                id="people/sam-kaur",
                type=NodeType.PERSON,
                title="Sam Kaur",
                acl=AclRef(ref="fs:corpus:public", sensitivity=Sensitivity.PUBLIC),
                relations=(
                    Edge(
                        predicate=Predicate.OWNS,
                        object="processes/vendor-renewal",
                        confidence=0.9,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ),
                    Edge(
                        predicate=Predicate.OWNS,
                        object="processes/vendor-renewal",
                        confidence=0.4,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ),
                ),
            )

    def test_llm_edge_without_evidence_rejected(self) -> None:
        with pytest.raises(ValueError, match="must carry evidence"):
            Edge(
                predicate=Predicate.OWNS,
                object="processes/vendor-renewal",
                confidence=0.9,
                provenance=Provenance.LLM,
                status=EdgeStatus.PROPOSED,
            )


class TestGates:
    """docs/ARCHITECTURE.md §11 — the mention-to-ownership drift guard."""

    def test_owns_never_auto_accepts_however_confident(self) -> None:
        status = decide_status(
            Predicate.OWNS,
            confidence=0.99,
            provenance=Provenance.LLM,
            evidence=(
                Evidence(node="documents/a-111111", span=(0, 10)),
                Evidence(node="documents/b-222222", span=(0, 10)),
            ),
        )
        assert status is EdgeStatus.PROPOSED

    def test_mentions_auto_accepts_above_threshold(self) -> None:
        assert (
            decide_status(
                Predicate.MENTIONS,
                confidence=0.9,
                provenance=Provenance.LLM,
                evidence=(Evidence(span=(0, 5)),),
            )
            is EdgeStatus.ACCEPTED
        )

    def test_mentions_below_threshold_proposes(self) -> None:
        assert (
            decide_status(
                Predicate.MENTIONS,
                confidence=0.5,
                provenance=Provenance.LLM,
                evidence=(Evidence(span=(0, 5)),),
            )
            is EdgeStatus.PROPOSED
        )

    def test_handoff_to_always_proposes(self) -> None:
        assert (
            decide_status(
                Predicate.HANDOFF_TO,
                confidence=1.0,
                provenance=Provenance.LLM,
                evidence=(Evidence(span=(0, 5)),),
            )
            is EdgeStatus.PROPOSED
        )

    def test_structural_edges_bypass_the_gate(self) -> None:
        assert (
            decide_status(
                Predicate.OWNS,
                confidence=0.1,
                provenance=Provenance.STRUCTURAL,
                evidence=(),
            )
            is EdgeStatus.ACCEPTED
        )


class TestAcl:
    def test_narrowest_of_empty_is_restricted(self) -> None:
        # Fail closed: a derived node with no discoverable inputs is not public.
        assert narrowest([]) is Sensitivity.RESTRICTED

    def test_narrowest_picks_most_restrictive(self) -> None:
        assert (
            narrowest([Sensitivity.PUBLIC, Sensitivity.RESTRICTED, Sensitivity.INTERNAL])
            is Sensitivity.RESTRICTED
        )

    def test_malformed_ref_rejected(self) -> None:
        with pytest.raises(ValueError, match="acl ref must be"):
            AclRef(ref="slack-channel-C0ENG", sensitivity=Sensitivity.INTERNAL)


class TestIds:
    def test_slug_folds_accents_rather_than_dropping_them(self) -> None:
        assert slugify("Zoë Ravel") == "zoe-ravel"

    def test_slug_is_stable_across_punctuation_noise(self) -> None:
        assert slugify("Eng standup — 2024/03/14") == "eng-standup-2024-03-14"

    def test_document_slug_stable_under_retitle(self) -> None:
        uri = "slack://T01/C0ENG/p1710403200"
        a = document_slug("Eng standup", uri)
        b = document_slug("Engineering standup", uri)
        assert a.split("-")[-1] == b.split("-")[-1]

    def test_round_trip_id(self) -> None:
        node_id = make_id("Person", "sam-kaur")
        assert node_id == "people/sam-kaur"
        assert split_id(node_id) == ("Person", "sam-kaur")

    def test_unknown_type_segment_rejected(self) -> None:
        with pytest.raises(ValueError, match="unknown type segment"):
            split_id("widgets/foo")


class TestThirdPartySubjects:
    """The `owns` bug: a Document is never the subject of a third-party relation.

    Before this, extraction produced `document --owns--> person`, which reads as
    "this document owns Owen Fitzgerald". Answers hid it because synthesis reads
    text, not edges — but traverse and read_node returned nonsense.
    """

    def _doc(self, relations: tuple[Edge, ...]) -> Frontmatter:
        return Frontmatter(
            id="documents/x-abc123",
            type=NodeType.DOCUMENT,
            title="x",
            acl=AclRef(ref="fs:corpus:public", sensitivity=Sensitivity.PUBLIC),
            source=SourceRef(
                connector="t", uri="file://x", external_id="x", content_sha256=SHA
            ),
            relations=relations,
        )

    def test_owns_without_a_subject_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="needs an explicit subject"):
            self._doc(
                (
                    Edge(
                        predicate=Predicate.OWNS,
                        object="people/owen",
                        confidence=0.9,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ),
                )
            )

    def test_owns_with_a_subject_is_accepted(self) -> None:
        fm = self._doc(
            (
                Edge(
                    predicate=Predicate.OWNS,
                    subject="people/owen",
                    object="processes/capacity-planning",
                    confidence=0.9,
                    provenance=Provenance.HUMAN,
                    status=EdgeStatus.ACCEPTED,
                ),
            )
        )
        edge = fm.relations[0]
        assert edge.resolve_subject(fm.id) == "people/owen"

    def test_mentions_needs_no_subject(self) -> None:
        fm = self._doc(
            (
                Edge(
                    predicate=Predicate.MENTIONS,
                    object="tools/netsuite",
                    confidence=1.0,
                    provenance=Provenance.HUMAN,
                    status=EdgeStatus.ACCEPTED,
                ),
            )
        )
        # Absent subject means "the document", which is correct for mentions.
        assert fm.relations[0].resolve_subject(fm.id) == fm.id

    def test_subject_survives_the_round_trip(self) -> None:
        node = Node(
            frontmatter=self._doc(
                (
                    Edge(
                        predicate=Predicate.OWNS,
                        subject="people/owen",
                        object="processes/capacity-planning",
                        confidence=0.9,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ),
                )
            ),
            body="",
        )
        text = dump_node(node)
        assert "subject: people/owen" in text
        assert parse_node(text) == node

    def test_same_predicate_and_object_differing_by_subject_is_not_a_duplicate(
        self,
    ) -> None:
        fm = self._doc(
            (
                Edge(
                    predicate=Predicate.OWNS,
                    subject="people/owen",
                    object="processes/capacity-planning",
                    confidence=0.9,
                    provenance=Provenance.HUMAN,
                    status=EdgeStatus.ACCEPTED,
                ),
                Edge(
                    predicate=Predicate.OWNS,
                    subject="people/sam-kaur",
                    object="processes/capacity-planning",
                    confidence=0.5,
                    provenance=Provenance.HUMAN,
                    status=EdgeStatus.PROPOSED,
                ),
            )
        )
        # Two people claiming the same process is a real disagreement worth
        # surfacing, not a duplicate to collapse.
        assert len(fm.relations) == 2

    def test_a_subjectful_self_edge_is_still_rejected(self) -> None:
        with pytest.raises(ValueError, match="self-edge"):
            self._doc(
                (
                    Edge(
                        predicate=Predicate.OWNS,
                        subject="people/owen",
                        object="people/owen",
                        confidence=0.9,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ),
                )
            )
