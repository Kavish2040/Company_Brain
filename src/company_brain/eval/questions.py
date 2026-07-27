"""The golden question set, derived from the corpus generator's own tables.

Hand-typed goldens rot. The corpus is regenerated from ``PROCESSES``, ``PEOPLE``,
``TEAMS`` and ``TOOLS``, so the questions and their expected evidence are built
from the same tables — rename a process and both move together. What is *not*
derived is the mapping from principal to visible source families
(:data:`VISIBLE_SOURCES`): that is restated here by hand precisely so a
disagreement with ``app.build_grants`` shows up as a failing test instead of a
quietly shrinking evaluation.

Expected evidence is a **substring** of a node ID, not an exact ID. Document IDs
carry a ``-<hash6>`` suffix derived from the source URI (``schemas/ids.py``), so
an exact ID would pin the goldens to a URI scheme they have no opinion about.
The substring is also what ``test_m1.py::SEEDED`` has always asserted, which
lets the ten M1 goldens move in here verbatim rather than being re-expressed.

Question classes carry different burdens:

* ``factual``, ``ownership``, ``temporal`` — answerable today. Regressions here
  are bugs.
* ``systemic`` — M4's actual target. These score badly at the point the harness
  lands, and that is the number the milestone has to move.
* ``unanswerable`` — the corpus genuinely cannot answer these. The metric is the
  refusal rate, and a *rising* score on the other classes bought by confabulating
  here is a loss, not a win.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from company_brain.corpus.generate import PEOPLE, PROCESSES, TEAMS, TOOLS
from company_brain.schemas.ids import slugify

# Source families. A node's family is derived from its ID, which is a corpus
# fact; the ACL engine plays no part in deriving it, so using it to check a leak
# does not beg the question.
DOCS: Final = "docs"
EMAIL: Final = "email"
SLACK_CHANNELS: Final = (
    "general",
    "engineering",
    "support",
    "finance",
    "leadership-comp",
)
KNOWN_FAMILIES: Final = frozenset({DOCS, EMAIL, *(f"slack:{c}" for c in SLACK_CHANNELS)})


class QuestionClass(StrEnum):
    FACTUAL = "factual"
    OWNERSHIP = "ownership"
    TEMPORAL = "temporal"
    SYSTEMIC = "systemic"
    UNANSWERABLE = "unanswerable"


@dataclass(frozen=True, slots=True)
class Golden:
    """One golden question.

    ``evidence`` is the set of evidence *kinds* the answer must rest on, each a
    node-ID substring. Recall is the fraction of them retrieved, so a question
    citing three kinds of evidence is not scored as three-quarters right for
    finding one meeting note.
    """

    id: str
    question: str
    qclass: QuestionClass
    evidence: tuple[str, ...] = ()
    seeded: bool = False

    @property
    def answerable(self) -> bool:
        return self.qclass is not QuestionClass.UNANSWERABLE


def source_of(node_id_or_pattern: str) -> str:
    """The source family a node ID (or an evidence substring) belongs to.

    Entity nodes — ``people/…``, ``processes/…`` — are derived from the docs
    tree and inherit its ACL ref, so they fall in ``docs``.
    """
    if node_id_or_pattern.startswith("documents/slack/"):
        return f"slack:{node_id_or_pattern.split('/')[2]}"
    if node_id_or_pattern.startswith("documents/email/"):
        return EMAIL
    return DOCS


# What each principal *should* be able to see, restated independently of
# `app.build_grants` and `corpus.generate.CHANNEL_MEMBERS`. The harness checks
# every retrieved and cited node against this, so a widened grant surfaces as a
# leak here even when the grant table thinks it is behaving.
VISIBLE_SOURCES: Final[dict[str, frozenset[str]]] = {
    "ceo": frozenset(
        {DOCS, EMAIL, *(f"slack:{c}" for c in SLACK_CHANNELS)},
    ),
    "support-lead": frozenset(
        {DOCS, EMAIL, "slack:general", "slack:engineering", "slack:support"},
    ),
    "eng-ic": frozenset({DOCS, EMAIL, "slack:general", "slack:engineering"}),
    "contractor": frozenset({"slack:general"}),
}


def visible_evidence(golden: Golden, principal: str) -> tuple[str, ...]:
    """The subset of a question's evidence that `principal` is allowed to reach.

    Recall is measured against this, never against the full set. Scoring the CEO
    and a contractor against the same denominator reports a permissions boundary
    as a quality regression, which is the exact confusion this harness exists to
    prevent.
    """
    allowed = VISIBLE_SOURCES[principal]
    return tuple(p for p in golden.evidence if source_of(p) in allowed)


# --- evidence-pattern builders ------------------------------------------
# Every document ID is `documents/<corpus dir>/<slugify(title)>-<hash6>`, so the
# patterns are built from the same names the generator writes.


def process_page(name: str) -> str:
    return f"documents/docs/processes/{slugify(name)}-"


def runbook(name: str) -> str:
    return f"documents/docx/{slugify(name)}-runbook-"


def policy(name: str) -> str:
    return f"documents/pdf/{slugify(name)}-policy-"


def decision_doc(name: str) -> str:
    return f"documents/docs/decisions/decision-adjust-{slugify(name)}-"


def meeting_notes(name: str) -> str:
    return f"documents/docs/meetings/{slugify(name)}-sync-"


def team_page(team: str) -> str:
    return f"documents/docs/teams/{slugify(team)}-"


def tool_page(slug: str) -> str:
    return f"documents/docs/tools/{slug}-"


def channel(name: str) -> str:
    return f"documents/slack/{name}/"


DIGESTS: Final = "documents/email/weekly-escalation-digest-"
PROCESS_PAGES: Final = "documents/docs/processes/"
DECISIONS: Final = "documents/docs/decisions/"
TOOL_PAGES: Final = "documents/docs/tools/"

# The six processes that also have a PDF policy (generate.py writes PROCESSES[:6]).
_WITH_POLICY: Final = frozenset(name for _, name, _, _ in PROCESSES[:6])


def _policies(name: str) -> tuple[str, ...]:
    return (policy(name),) if name in _WITH_POLICY else ()


# --- the ten M1 goldens, verbatim ---------------------------------------
# Same question strings and same expected substrings as
# `tests/acceptance/test_m1.py::SEEDED`. They live here so "no regression
# against the M1 goldens" is a measurement rather than a claim; a test asserts
# the two lists still agree.
_SEEDED: Final[tuple[tuple[str, str, QuestionClass], ...]] = (
    ("who owns vendor renewals?", "vendor-renewal", QuestionClass.OWNERSHIP),
    ("who is responsible for incident response?", "incident-response", QuestionClass.OWNERSHIP),
    ("what is the customer escalation process?", "customer-escalation", QuestionClass.FACTUAL),
    ("who owns quarterly close?", "quarterly-close", QuestionClass.OWNERSHIP),
    (
        "what does the release sign-off process involve?",
        "release-sign-off",
        QuestionClass.FACTUAL,
    ),
    ("which team owns security review?", "security-review", QuestionClass.OWNERSHIP),
    ("what is Project Snowflake?", "snowflake", QuestionClass.FACTUAL),
    ("who handles refund approval?", "refund-approval", QuestionClass.OWNERSHIP),
    ("what happens during employee onboarding?", "onboarding", QuestionClass.FACTUAL),
    ("who owns capacity planning?", "capacity-planning", QuestionClass.OWNERSHIP),
)


def _seeded() -> list[Golden]:
    return [
        Golden(
            id=f"m1-{i:02d}",
            question=question,
            qclass=qclass,
            evidence=(expected,),
            seeded=True,
        )
        for i, (question, expected, qclass) in enumerate(_SEEDED)
    ]


def _ownership() -> list[Golden]:
    out: list[Golden] = []
    for slug, name, _owner, team in PROCESSES:
        out.append(
            Golden(
                id=f"own-named-{slug}",
                question=f"who is the named owner of {name.lower()}?",
                qclass=QuestionClass.OWNERSHIP,
                evidence=(process_page(name), runbook(name), *_policies(name)),
            )
        )
        out.append(
            Golden(
                id=f"own-team-{slug}",
                question=f"which team is accountable for {name.lower()}?",
                qclass=QuestionClass.OWNERSHIP,
                evidence=(process_page(name), team_page(team)),
            )
        )
    for team in TEAMS:
        out.append(
            Golden(
                id=f"own-portfolio-{slugify(team)}",
                question=f"which processes does the {team} team own?",
                qclass=QuestionClass.OWNERSHIP,
                evidence=(team_page(team),),
            )
        )
    return out


def _factual() -> list[Golden]:
    out: list[Golden] = []
    for slug, name, _description in TOOLS:
        out.append(
            Golden(
                id=f"fact-tool-{slug}",
                question=f"what is {name} used for at Meridian?",
                qclass=QuestionClass.FACTUAL,
                evidence=(tool_page(slug),),
            )
        )
    for person in PEOPLE:
        out.append(
            Golden(
                id=f"fact-role-{person.slug}",
                question=f"what is {person.name}'s role at Meridian?",
                qclass=QuestionClass.FACTUAL,
                evidence=(team_page(person.team),),
            )
        )
    for team in TEAMS:
        out.append(
            Golden(
                id=f"fact-roster-{slugify(team)}",
                question=f"who is on the {team} team?",
                qclass=QuestionClass.FACTUAL,
                evidence=(team_page(team),),
            )
        )
    for _slug, name, _owner, _team in PROCESSES[:6]:
        out.append(
            Golden(
                id=f"fact-steps-{slugify(name)}",
                question=f"what are the steps in the {name.lower()} process?",
                qclass=QuestionClass.FACTUAL,
                evidence=(process_page(name), runbook(name)),
            )
        )
    # The three traps the generator plants on purpose (generate.py docstring):
    # a name collision, an ambiguous person, and a shared inbox that is not one.
    out.extend(
        [
            Golden(
                id="fact-trap-snowflake",
                question="is Snowflake a vendor or an internal project?",
                qclass=QuestionClass.FACTUAL,
                evidence=("documents/docs/projects/project-snowflake-", tool_page("snowflake")),
            ),
            Golden(
                id="fact-trap-sam-k",
                question="which Sam confirmed the NetSuite renewal is on track?",
                qclass=QuestionClass.FACTUAL,
                evidence=(
                    "documents/docs/notes/vendor-sync-notes-",
                    "documents/docs/people/note-on-names-",
                ),
            ),
            Golden(
                id="fact-trap-shared-inbox",
                question="who sends the weekly escalation digest?",
                qclass=QuestionClass.FACTUAL,
                evidence=(DIGESTS,),
            ),
            Golden(
                id="fact-two-sams",
                question="how do I tell Sam Kaur and Sam Kelly apart?",
                qclass=QuestionClass.FACTUAL,
                evidence=("documents/docs/people/note-on-names-",),
            ),
        ]
    )
    return out


def _temporal() -> list[Golden]:
    out = [
        Golden(
            id=f"time-decision-{slug}",
            question=f"what was decided about {name.lower()}, and when?",
            qclass=QuestionClass.TEMPORAL,
            evidence=(decision_doc(name),),
        )
        for slug, name, _owner, _team in PROCESSES
    ]
    out.extend(
        [
            Golden(
                id="time-netsuite-renewal",
                question="when does the NetSuite renewal fall due?",
                qclass=QuestionClass.TEMPORAL,
                evidence=(tool_page("netsuite"), channel("finance")),
            ),
            Golden(
                id="time-vendor-renewal-syncs",
                question="when did the vendor renewal syncs happen?",
                qclass=QuestionClass.TEMPORAL,
                evidence=(meeting_notes("Vendor renewal"),),
            ),
            Golden(
                id="time-recent-decisions",
                question="which decisions were recorded in February 2024?",
                qclass=QuestionClass.TEMPORAL,
                evidence=(DECISIONS,),
            ),
            Golden(
                id="time-release-signoff-change",
                question="what is the most recent decision about release sign-off?",
                qclass=QuestionClass.TEMPORAL,
                evidence=(decision_doc("Release sign-off"),),
            ),
        ]
    )
    return out


def _systemic() -> list[Golden]:
    out = [
        Golden(
            id=f"sys-handoff-{slug}",
            question=f"what is the handoff path for {name.lower()}, and where does it stall?",
            qclass=QuestionClass.SYSTEMIC,
            evidence=(process_page(name), runbook(name)),
        )
        for slug, name, _owner, _team in PROCESSES
    ]
    out.extend(
        [
            # The pitch question itself (ROADMAP M4).
            Golden(
                id="sys-support-eng-handoffs",
                question=("where are handoffs between Support and Engineering breaking down?"),
                qclass=QuestionClass.SYSTEMIC,
                evidence=(channel("support"), DIGESTS, "documents/docs/meetings/"),
            ),
            Golden(
                id="sys-bounce-rate",
                question="how often do tickets bounce back from Engineering to Support?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(DIGESTS, channel("support")),
            ),
            Golden(
                id="sys-single-owner",
                question="which processes have a single named owner and no backup?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(PROCESS_PAGES,),
            ),
            Golden(
                id="sys-slack-only",
                question="which processes are documented only in a Slack thread?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(channel("engineering"), channel("support")),
            ),
            Golden(
                id="sys-ownerless-tools",
                question="which tools have no owning team?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(TOOL_PAGES,),
            ),
            Golden(
                id="sys-finance-handoffs",
                question="which teams hand work off to Finance, and for what?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(PROCESS_PAGES, team_page("Finance")),
            ),
            Golden(
                id="sys-security-review-blocking",
                question="which processes are blocked waiting on security review?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(process_page("Security review"), channel("finance")),
            ),
            Golden(
                id="sys-escalation-load",
                question="which team receives the most escalations?",
                qclass=QuestionClass.SYSTEMIC,
                evidence=(channel("support"), DIGESTS),
            ),
        ]
    )
    return out


# Nothing in the corpus answers these. The corpus states no headcount, no
# manager relationships, no prices, no office locations and no dates past the
# generated window, so a confident answer to any of them is a fabrication.
_UNANSWERABLE: Final[tuple[tuple[str, str], ...]] = (
    ("unans-revenue", "what is Meridian's 2027 revenue forecast?"),
    ("unans-payroll", "who owns the payroll process?"),
    ("unans-cfo", "who is Meridian's CFO?"),
    ("unans-headcount", "how many employees does Meridian have?"),
    ("unans-oncall", "what is the on-call rotation schedule for next month?"),
    ("unans-snowflake-price", "what does the Snowflake contract cost per year?"),
    ("unans-zendesk-limit", "what is the Zendesk API rate limit?"),
    ("unans-board", "when is the next board meeting?"),
    ("unans-manager", "who is Mei Tanaka's manager?"),
    ("unans-office", "which office is the Finance team based in?"),
    ("unans-language", "what programming language is the ingest service written in?"),
    ("unans-budget", "who approved the 2025 budget?"),
    ("unans-churn", "which customers churned in Q4?"),
    ("unans-penalty", "what is the penalty clause in the Zendesk contract?"),
)


def _unanswerable() -> list[Golden]:
    return [
        Golden(id=qid, question=question, qclass=QuestionClass.UNANSWERABLE)
        for qid, question in _UNANSWERABLE
    ]


def _build() -> tuple[Golden, ...]:
    goldens = [
        *_seeded(),
        *_ownership(),
        *_factual(),
        *_temporal(),
        *_systemic(),
        *_unanswerable(),
    ]
    ids = [g.id for g in goldens]
    if len(set(ids)) != len(ids):
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"duplicate golden ids: {duplicates}")
    # An evidence pattern whose family is unrecognised is invisible to *every*
    # principal, so it silently drops out of recall instead of failing. Caught
    # here, at import, rather than showing up as an unexplained score.
    unknown = sorted(
        {
            f"{g.id}: {p} -> {source_of(p)}"
            for g in goldens
            for p in g.evidence
            if source_of(p) not in KNOWN_FAMILIES
        }
    )
    if unknown:
        raise ValueError(f"evidence patterns in no known source family: {unknown}")
    return tuple(sorted(goldens, key=lambda g: g.id))


GOLDENS: Final[tuple[Golden, ...]] = _build()


def by_class(qclass: QuestionClass) -> tuple[Golden, ...]:
    return tuple(g for g in GOLDENS if g.qclass is qclass)
