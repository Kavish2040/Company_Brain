"""Deterministic generator for the synthetic company corpus.

Models Meridian Logistics, ~60 people, across .md / .eml / Slack JSON / .docx /
.pdf. Everything is seeded from a fixed PRNG and fixed dates, so regenerating
produces a byte-identical tree — the corpus itself has to satisfy the same
determinism bar as the pipeline that reads it.

Three messy cases are planted on purpose, because a corpus we authored is a
corpus we unconsciously made tractable (ROADMAP, sequencing notes):

1. **Sam Kaur vs. Sam Kelly** — both appear as "Sam K.", they work together, and
   co-occurrence features make them *more* confusable, not less (§10.2).
2. **support@meridian.example** — a shared inbox that authors documents and will
   attract ownership edges as if it were a person (§10.2).
3. **Snowflake** — the warehouse vendor and an internal project codename, same
   string, different type (§10.2).
"""

from __future__ import annotations

import json
import random
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

SEED: Final = 20240314
EPOCH: Final = datetime(2024, 1, 8, 9, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class Person:
    slug: str
    name: str
    email: str
    slack_id: str
    team: str
    role: str


PEOPLE: Final[tuple[Person, ...]] = (
    Person(
        "sam-kaur",
        "Sam Kaur",
        "sam.kaur@meridian.example",
        "U01SAMK",
        "Finance",
        "Finance Lead",
    ),
    Person(
        "sam-kelly",
        "Sam Kelly",
        "sam.kelly@meridian.example",
        "U01SAMY",
        "Engineering",
        "Backend Engineer",
    ),
    Person(
        "priya-raman",
        "Priya Raman",
        "priya@meridian.example",
        "U02PRIY",
        "Engineering",
        "VP Engineering",
    ),
    Person(
        "dev-oyelaran",
        "Dev Oyelaran",
        "dev@meridian.example",
        "U03DEVO",
        "Support",
        "Support Lead",
    ),
    Person(
        "mei-tanaka",
        "Mei Tanaka",
        "mei@meridian.example",
        "U04MEIT",
        "Support",
        "Support Engineer",
    ),
    Person(
        "ana-brito", "Ana Brito", "ana@meridian.example", "U05ANAB", "Finance", "Controller"
    ),
    Person(
        "tom-whelan",
        "Tom Whelan",
        "tom@meridian.example",
        "U06TOMW",
        "Engineering",
        "Platform Engineer",
    ),
    Person(
        "zoe-ravel",
        "Zoë Ravel",
        "zoe@meridian.example",
        "U07ZOER",
        "Product",
        "Head of Product",
    ),
    Person(
        "owen-fitz", "Owen Fitzgerald", "owen@meridian.example", "U08OWEN", "Engineering", "SRE"
    ),
    Person(
        "nadia-hassan", "Nadia Hassan", "nadia@meridian.example", "U09NADH", "Product", "PM"
    ),
)

TEAMS: Final = ("Engineering", "Support", "Finance", "Product")

TOOLS: Final[tuple[tuple[str, str, str], ...]] = (
    ("netsuite", "NetSuite", "Finance system of record; annual renewal each April."),
    ("zendesk", "Zendesk", "Customer support ticketing."),
    (
        "snowflake",
        "Snowflake",
        "Data warehouse vendor. NOT the internal project of the same name.",
    ),
    ("pagerduty", "PagerDuty", "On-call paging."),
    ("linear", "Linear", "Engineering issue tracking."),
    ("datadog", "Datadog", "Observability and alerting."),
)

# Curated up front rather than discovered. Open-vocabulary process extraction
# produces hundreds of near-duplicate nodes (§10.3); the extractor matches
# against this list instead of inventing names.
PROCESSES: Final[tuple[tuple[str, str, str, str], ...]] = (
    ("vendor-renewal", "Vendor renewal", "sam-kaur", "Finance"),
    ("incident-response", "Incident response", "owen-fitz", "Engineering"),
    ("customer-escalation", "Customer escalation", "dev-oyelaran", "Support"),
    ("quarterly-close", "Quarterly close", "ana-brito", "Finance"),
    ("release-signoff", "Release sign-off", "priya-raman", "Engineering"),
    ("onboarding", "Employee onboarding", "zoe-ravel", "Product"),
    ("security-review", "Security review", "tom-whelan", "Engineering"),
    ("capacity-planning", "Capacity planning", "owen-fitz", "Engineering"),
    ("refund-approval", "Refund approval", "ana-brito", "Finance"),
    ("data-request", "Customer data request", "mei-tanaka", "Support"),
)

# The private one is the ACL canary: an answer that cites it for any principal
# other than the CEO is a leak, and the acceptance suite asserts exactly that.
CHANNELS: Final[tuple[tuple[str, str, str], ...]] = (
    ("C0ENG", "engineering", "internal"),
    ("C0SUP", "support", "internal"),
    ("C0FIN", "finance", "restricted"),
    ("C0GEN", "general", "public"),
    ("C0LEAD", "leadership-comp", "restricted"),
)

SLACK_DAYS: Final = 19

# Channel membership, canonically, keyed by channel name.
#
# This is the *only* declaration of who is in which channel. `app.build_grants`
# reads it to seed the grant table and `connectors.simulated` reads it to build
# the workspace the sync engine reconciles against. They used to hold separate
# hardcoded copies that happened to agree; nothing detected disagreement, and a
# silent disagreement here reads as a mass grant revocation on the next sync.
#
# Note the vocabulary: these are *principal* ids (app.PRINCIPALS), not the
# corpus's `PEOPLE` slugs. The synthetic principals are roles that stand in for
# people; keeping them here rather than in `app.py` is what lets the connector
# see the same table without importing the composition root.
CHANNEL_MEMBERS: Final[dict[str, frozenset[str]]] = {
    "general": frozenset({"ceo", "support-lead", "eng-ic", "contractor"}),
    "engineering": frozenset({"ceo", "support-lead", "eng-ic"}),
    "support": frozenset({"ceo", "support-lead"}),
    "finance": frozenset({"ceo"}),
    # The canary: only the CEO. The acceptance suite's leak test turns on it.
    "leadership-comp": frozenset({"ceo"}),
}


def channel_id(name: str) -> str:
    """The Slack id for a channel name."""
    return next(cid for cid, channel, _ in CHANNELS if channel == name)


def channel_tier(name: str) -> str:
    return next(tier for _, channel, tier in CHANNELS if channel == name)


def channels_for(principal_id: str) -> tuple[str, ...]:
    """Every channel name `principal_id` is a member of, sorted."""
    return tuple(
        sorted(name for name, members in CHANNEL_MEMBERS.items() if principal_id in members)
    )


def slack_export_path(channel: str, date: str) -> str:
    """Corpus-relative path of one channel-day export."""
    return f"slack/{channel}/{date}.json"


def slack_export_uri(channel: str, date: str) -> str:
    """The artifact URI for one channel-day export.

    The simulated connector serves the *same* URI as the on-disk corpus, because
    in the simulation they are the same artifact seen two ways: `cb ingest` reads
    the export file, `cb sync` reads the workspace that produced it. Node IDs
    derive from this URI (invariant 12), so sharing it is what makes a sync over
    an already-ingested corpus a no-op instead of a second copy of every channel.
    A real Slack connector would serve `slack://…` and own its nodes outright.
    """
    return f"file://corpus/{slack_export_path(channel, date)}"


def slack_export_bytes(messages: list[dict[str, object]]) -> bytes:
    """Serialize a channel-day. The one place these bytes are produced.

    Both the corpus writer and the simulated connector go through here: the
    content hash is what change detection turns on, so two encoders would mean
    phantom updates and a busted extraction cache.
    """
    return json.dumps(messages, indent=2, sort_keys=True).encode() + b"\n"


def normalize_zip(data: bytes) -> bytes:
    """Rewrite a zip with fixed entry timestamps and sorted names.

    A .docx *is* a zip, and zip entries carry the local mtime at write time, so
    python-docx emits different bytes on every save even for identical content.
    Without this the corpus is not reproducible and the M1 acceptance test can
    never pass — a failure mode invisible until you diff two generations.
    """
    import io
    import zipfile

    source = zipfile.ZipFile(io.BytesIO(data))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as target:
        for name in sorted(source.namelist()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            target.writestr(info, source.read(name))
    return buffer.getvalue()


def _person(slug: str) -> Person:
    return next(p for p in PEOPLE if p.slug == slug)


def _stamp(day_offset: int, hour: int = 9, minute: int = 0) -> datetime:
    return EPOCH + timedelta(days=day_offset, hours=hour - 9, minutes=minute)


def _rfc822(when: datetime) -> str:
    return when.strftime("%a, %d %b %Y %H:%M:%S +0000")


def minimal_pdf(title: str, lines: list[str]) -> bytes:
    """Hand-rolled single-page PDF.

    Written by hand rather than pulled from a library because the corpus must be
    byte-reproducible, and PDF writers embed creation timestamps and generator
    strings that would change on every run.
    """

    def esc(text: str) -> str:
        clean = "".join(c if 32 <= ord(c) < 127 else "?" for c in text)
        return clean.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

    content_lines = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
    content_lines.append(f"({esc(title)}) Tj")
    for line in lines:
        content_lines.append("T*")
        content_lines.append(f"({esc(line)}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("ascii")

    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
        b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>",
        b"<</Length " + str(len(stream)).encode() + b">>\nstream\n" + stream + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer\n<</Size {len(objects) + 1}/Root 1 0 R>>\nstartxref\n{xref_at}\n".encode()
    out += b"%%EOF\n"
    return bytes(out)


def _slack_day(
    channel: str, tier: str, day: int, rng: random.Random
) -> list[dict[str, object]]:
    speakers = [p for p in PEOPLE if channel != "finance" or p.team == "Finance"]
    if channel == "leadership-comp":
        speakers = [_person("priya-raman"), _person("sam-kaur")]
    if not speakers:
        speakers = list(PEOPLE)

    topics = {
        "engineering": [
            "Deploy for the {proc} change is queued behind the release sign-off.",
            "The {tool} alert fired again overnight — third time this week.",
            "Handing the {proc} ticket over to Support, they own the customer comms.",
            "Can someone from Finance confirm the {tool} renewal date?",
        ],
        "support": [
            "Escalating this to Engineering — it's a {tool} integration bug, not config.",
            "Customer is asking about the {proc} timeline again.",
            "This is the fourth ticket bounced back from Engineering on {proc}.",
            "Looping in Finance for the refund side of {proc}.",
        ],
        "finance": [
            "The {tool} renewal lands in April. I own that end to end.",
            "{proc} is blocked until Engineering signs off on the security review.",
            "Reminder: {proc} closes Friday.",
        ],
        "general": [
            "Welcome to the team! Onboarding docs are in Drive.",
            "All-hands moved to Thursday.",
            "Reminder that {proc} kicks off next week.",
        ],
        "leadership-comp": [
            "Compensation bands for the Engineering ladder need revisiting before Q3.",
            "Let's keep the comp discussion in this channel only.",
        ],
    }[channel]

    messages: list[dict[str, object]] = []
    base = _stamp(day, 9 + rng.randrange(0, 6), rng.randrange(0, 59))
    count = rng.randrange(2, 5)
    for i in range(count):
        speaker = rng.choice(speakers)
        proc = rng.choice(PROCESSES)
        tool = rng.choice(TOOLS)
        text = rng.choice(topics).format(proc=proc[1], tool=tool[1])
        ts = base + timedelta(minutes=7 * i)
        messages.append(
            {
                "type": "message",
                "user": speaker.slack_id,
                "user_profile": {"real_name": speaker.name},
                "text": text,
                "ts": f"{ts.timestamp():.6f}",
            }
        )
    return messages


def slack_days(
    rng: random.Random | None = None,
) -> Iterator[tuple[str, str, str, list[dict[str, object]]]]:
    """Every `(channel, tier, date, messages)` in the workspace's history.

    Shared by `generate()`, which writes these to disk, and by
    `connectors.simulated`, which serves them as a live workspace. One producer
    is the point: the simulated source used to fabricate its own one-line
    messages at its own epoch, so `cb sync` bolted a second, junk copy of every
    channel onto a store that already held the real ones.

    `rng` exists because the corpus generator's later sections continue the same
    PRNG stream; callers who only want the Slack half get a fresh one, which
    yields the same days because Slack is generated first.
    """
    stream = rng if rng is not None else random.Random(SEED)
    for _cid, channel, tier in CHANNELS:
        for day in range(SLACK_DAYS):
            messages = _slack_day(channel, tier, day, stream)
            if not messages:
                continue
            yield channel, tier, _stamp(day).date().isoformat(), messages


def generate(out_dir: Path) -> list[Path]:
    """Write the corpus. Returns every path written, sorted."""
    rng = random.Random(SEED)
    written: list[Path] = []

    def write(rel: str, data: bytes) -> None:
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        written.append(path)

    # --- Slack: 5 channels x 19 days -----------------------------------
    for channel, _tier, date, messages in slack_days(rng):
        write(slack_export_path(channel, date), slack_export_bytes(messages))

    # --- Markdown: one page per process, plus team pages ---------------
    for slug, name, owner_slug, team in PROCESSES:
        owner = _person(owner_slug)
        body = f"""# {name}

**Owner:** {owner.name} ({owner.email})
**Team:** {team}

## Purpose

The {name.lower()} process governs how Meridian handles {name.lower()} requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in {rng.choice(TOOLS)[1]}.
2. {team} triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. {owner.name} signs off before the request is closed.

## Handoffs

- {team} hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
"""
        write(f"docs/processes/{slug}.md", body.encode())

    for team in TEAMS:
        members = [p for p in PEOPLE if p.team == team]
        roster = "\n".join(f"- {p.name} — {p.role} ({p.email})" for p in members)
        owned = [p for p in PROCESSES if p[3] == team]
        owns = "\n".join(f"- {n} (owner: {_person(o).name})" for _, n, o, _ in owned)
        write(
            f"docs/teams/{team.lower()}.md",
            f"# {team}\n\n## Members\n\n{roster}\n\n## Processes owned\n\n{owns}\n".encode(),
        )

    for slug, name, description in TOOLS:
        write(
            f"docs/tools/{slug}.md",
            f"# {name}\n\n{description}\n\nOwned by the {rng.choice(TEAMS)} team.\n".encode(),
        )

    # The name-collision trap: same string, different type.
    write(
        "docs/projects/snowflake.md",
        b"# Project Snowflake\n\nInternal codename for the Q2 warehouse migration.\n"
        b"Not to be confused with Snowflake the vendor, which is the target\n"
        b"platform for this project. Led by Tom Whelan.\n",
    )

    # --- Email threads --------------------------------------------------
    for i in range(28):
        sender = PEOPLE[rng.randrange(len(PEOPLE))]
        recipient = PEOPLE[rng.randrange(len(PEOPLE))]
        proc = rng.choice(PROCESSES)
        when = _stamp(rng.randrange(0, 60), 10 + rng.randrange(0, 7))
        subject = f"Re: {proc[1]} — {rng.choice(['status', 'approval needed', 'question'])}"
        text = (
            f"Hi {recipient.name.split()[0]},\n\n"
            f"Following up on {proc[1].lower()}. {_person(proc[2]).name} owns this "
            f"process, but the {rng.choice(TOOLS)[1]} step is blocked on your team.\n\n"
            f"Can you confirm by Friday?\n\nThanks,\n{sender.name}\n"
        )
        eml = (
            f"From: {sender.name} <{sender.email}>\n"
            f"To: {recipient.name} <{recipient.email}>\n"
            f"Subject: {subject}\n"
            f"Date: {_rfc822(when)}\n"
            f"Message-ID: <{i:04d}@meridian.example>\n"
            f"Content-Type: text/plain; charset=utf-8\n\n{text}"
        )
        write(f"email/thread-{i:03d}.eml", eml.encode())

    # Shared-inbox trap: authors documents, is not a person.
    for i in range(4):
        when = _stamp(20 + i, 11)
        eml = (
            f"From: Meridian Support <support@meridian.example>\n"
            f"To: Dev Oyelaran <dev@meridian.example>\n"
            f"Subject: Weekly escalation digest {i + 1}\n"
            f"Date: {_rfc822(when)}\n"
            f"Content-Type: text/plain; charset=utf-8\n\n"
            f"Automated digest. {3 + i} escalations were handed to Engineering "
            f"this week; {i} bounced back to Support unresolved.\n"
        )
        write(f"email/digest-{i:03d}.eml", eml.encode())

    # --- PDFs -----------------------------------------------------------
    for i, (slug, name, owner_slug, team) in enumerate(PROCESSES[:6]):
        owner = _person(owner_slug)
        write(
            f"pdf/{slug}-policy.pdf",
            minimal_pdf(
                f"{name} Policy",
                [
                    f"Owner: {owner.name}",
                    f"Team: {team}",
                    "",
                    f"This policy governs {name.lower()} at Meridian Logistics.",
                    "Approvals must be recorded before closure.",
                    f"Reviewed {_stamp(i * 5).date().isoformat()}.",
                ],
            ),
        )

    # --- Word documents --------------------------------------------------
    # python-docx stamps core properties with the current time, so created/
    # modified are pinned explicitly — otherwise the corpus would differ on
    # every regeneration and the acceptance test could never pass.
    try:
        import docx

        for i, (slug, name, owner_slug, team) in enumerate(PROCESSES):
            owner = _person(owner_slug)
            document = docx.Document()
            document.add_heading(f"{name} — runbook", level=1)
            document.add_paragraph(f"Owner: {owner.name} ({owner.email})")
            document.add_paragraph(f"Owning team: {team}")
            document.add_heading("Escalation path", level=2)
            for step in (
                f"{team} triage",
                "Cross-team handoff if root cause sits elsewhere",
                f"Sign-off by {owner.name}",
            ):
                document.add_paragraph(step, style="List Bullet")
            table = document.add_table(rows=3, cols=2)
            table.rows[0].cells[0].text = "Stage"
            table.rows[0].cells[1].text = "Owner"
            table.rows[1].cells[0].text = "Triage"
            table.rows[1].cells[1].text = team
            table.rows[2].cells[0].text = "Sign-off"
            table.rows[2].cells[1].text = owner.name

            core = document.core_properties
            core.title = f"{name} runbook"
            core.author = owner.name
            core.created = _stamp(i * 3).replace(tzinfo=None)
            core.modified = _stamp(i * 3 + 1).replace(tzinfo=None)
            core.revision = 1
            core.last_modified_by = owner.name

            import io

            buffer = io.BytesIO()
            document.save(buffer)
            write(f"docx/{slug}-runbook.docx", normalize_zip(buffer.getvalue()))
    except ImportError:  # pragma: no cover
        pass

    # --- Meeting notes ----------------------------------------------------
    for i in range(24):
        proc = PROCESSES[i % len(PROCESSES)]
        attendees = rng.sample(PEOPLE, 4)
        when = _stamp(2 + i * 2, 15)
        names = ", ".join(p.name for p in attendees)
        write(
            f"docs/meetings/{when.date().isoformat()}-{proc[0]}.md",
            f"""# {proc[1]} sync — {when.date().isoformat()}

**Attendees:** {names}

## Notes

- {attendees[0].name} raised that {proc[1].lower()} is still blocked on
  {rng.choice(TOOLS)[1]}.
- {_person(proc[2]).name} confirmed they own the process.
- Handoff from {attendees[1].team} to {attendees[2].team} is unclear; two
  tickets bounced back last week.

## Actions

- {attendees[3].name} to document the handoff boundary.
""".encode(),
        )

    # --- The Sam K. ambiguity trap --------------------------------------
    kaur, kelly = _person("sam-kaur"), _person("sam-kelly")
    write(
        "docs/notes/vendor-sync-notes.md",
        b"""# Vendor sync notes

Attendees: Sam K., Priya Raman, Ana Brito

Sam K. confirmed the NetSuite renewal is on track for April. Sam is also
picking up the Snowflake contract review.

Action: Sam K. to circulate the renewal calendar.
""",
    )
    write(
        "docs/notes/platform-sync-notes.md",
        b"""# Platform sync notes

Attendees: Sam K., Tom Whelan, Owen Fitzgerald

Sam K. is migrating the ingest workers off the legacy queue. Sam flagged that
Project Snowflake will need a schema freeze first.

Action: Sam K. to write the migration RFC.
""",
    )
    write(
        "docs/people/disambiguation.md",
        f"""# Note on names

Two people at Meridian go by "Sam K.":

- {kaur.name} ({kaur.email}), {kaur.role}, {kaur.team}
- {kelly.name} ({kelly.email}), {kelly.role}, {kelly.team}

They work together on Project Snowflake, so context alone is often not enough
to tell them apart.
""".encode(),
    )

    # --- Decisions -------------------------------------------------------
    for i in range(10):
        proc = PROCESSES[i % len(PROCESSES)]
        when = _stamp(5 + i * 4, 14)
        write(
            f"docs/decisions/{when.date().isoformat()}-{proc[0]}.md",
            f"""# Decision: adjust {proc[1].lower()}

**Date:** {when.date().isoformat()}
**Decided by:** {_person(proc[2]).name}
**Status:** accepted

## Context

The existing {proc[1].lower()} process was taking too long.

## Decision

{_person(proc[2]).name} will own {proc[1].lower()} going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the {proc[3]} team page.
""".encode(),
        )

    return sorted(written)
