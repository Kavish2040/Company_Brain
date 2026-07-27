---
id: documents/gdrive/1vztLkTRfEeZIzgSdXf9KJxLvsZUX8p1R/paramount-meridian-case-study-final-76bc1c
type: Document
title: Paramount_Meridian_Case_Study Final
status: active
acl:
  ref: gdrive:folder:1vztLkTRfEeZIzgSdXf9KJxLvsZUX8p1R
  sensitivity: public
source:
  connector: gdrive
  uri: https://drive.google.com/file/d/1-lkcg26IWScYKsNZXR0nEHqPRPen_QCd
  external_id: 1-lkcg26IWScYKsNZXR0nEHqPRPen_QCd
  external_version: '12'
  content_sha256: 63a046c6d27283c9a3b971efa02e68c24da8c87be6231e9e398814ba27c36a07
timestamps:
  created: '2026-07-23T03:14:35.644000Z'
  modified: '2026-07-23T03:15:18.074000Z'
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 13b7feccf8e7daafde618b3eb50cc944
  status: accepted
---

 CONFIDENTIAL · CLIENT CASE STUDY https://www.meridiananalytics.app/

CLIENT
 Paramount, Networks, Streaming & Studios (illustrative)
PRODUCT
 Meridian, Audience Journey Analytics
ENGAGEMENT
 Cross-platform viewership demonstration panel
PREPARED BY
 Prometheus Innovations, Inc.
CLASSIFICATION
 Confidential
DATA STATUS
 Mock / synthetic test data, not real participant data

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 ABOUT THIS DOCUMENT

Contents
This case study documents how Meridian , the audience journey analytics product from Prometheus
Innovations,

reconstructs

the

real

cross-platform

path

to

tune-in

for

a

slate

of

television

titles.

It

walks

through

the

problem

Meridian

solves,

why

last-click

attribution

misses

the

decision,

how

the

companion

app

captures

and

protects

participant

data

on-device,

the

demonstration

panel

that

produced

the

figures

shown

here,

a

section

by

section

reading

of

the

results,

and

how

the

platform

turns

all

of

it

into

decisions.

01 Executive Summary 3
02 The Problem: The Decision Happens Before the Last Click 4
03 How Meridian Works 5
04 Inside the Companion App: Capture & Privacy Architecture 6 The consent model: journey windows 7 What the engine captures, on-device 7 Where the data lives, and what reaches the cloud 8 05 Methodology & the Demonstration Panel 9
06 What the Data Revealed 11 The cross-platform path to tune-in 11 Where attention actually went 12 Attention-verified completion 13 Fan attention & conversation 13 07 The Meridian Platform 16

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 2 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 01 · OVERVIEW

Executive Summary
Studios, networks and streamers can measure the minutes watched inside their own apps, but not
the

journey

that

produced

them.

Discovery

now

happens

almost

entirely

off-platform:

in

YouTube

trailers,

TikTok

edits,

Reddit

threads,

group

chats

and

Google

searches.

By

the

time

a

viewer

presses

play,

the

path

that

drove

tune-in

is

already

invisible

to

first-party

analytics,

and

surveys

capture

only

what

audiences

think

they

remember.

Prometheus Innovations built Meridian to close that gap. Meridian is a consent-first, on-device
measurement

platform

that

reconstructs

the

real

cross-platform

path

to

tune-in,

covering

discovery,

viewing,

drop-off

and

conversation,

rolled

up

across

a

recruited

cohort

rather

than

a

single

anecdote.

It

is

the

software,

not

the

panel:

a

native

desktop

companion

app

that

recruited

viewers

choose

to

run,

which

turns

explicit,

consented

capture

windows

into

structured,

comparable

behaviour

around

a

title.

To demonstrate the platform on a realistic slate, we modeled a panel spanning 11 shows and 41
enrolled

participants
,

from

Survivor

and

Big

Brother

to

NCIS
,

South

Park

and

Star

Trek
.

In

the

captured

window

the

panel

produced

146

cross-platform

sessions

and

more

than

six

hours

of

attention-verified

activity
,

surfacing

the

exact

platforms

that

carried

each

title

from

first

exposure

to

fan

conversation.

The

figures

below

are

illustrative,

generated

to

exercise

the

full

reporting

surface.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 3 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 02 · THE PROBLEM

The Decision Happens Before the Last Click
Inside a studio, network or streamer, every team that lives or dies by tune-in is steering with a partial
map.

Marketing

spends

against

guesses

about

where

audiences

actually

discover

shows.

Ad-sales

pitches

reach

without

proof

of

what

those

audiences

watch

elsewhere.

Programming

greenlights

on

gut,

with

no

view

of

where

viewers

go

when

they

leave.

The

causes

are

structural,

not

a

matter

of

effort:

• Discovery happens off your platform. The trailer, the edit, the recap, the friend's text and the
search

that

drives

tune-in

all

happen

on

surfaces

you

do

not

own

and

cannot

instrument.
 • Your analytics stop at one wall. First-party telemetry sees viewing inside your app, and
nothing

of

the

cross-platform

path

that

led

there.
 • Surveys ask for a memory that does not exist. Audiences cannot reliably reconstruct a
journey

that

spanned

six

apps

in

a

single

evening,

so

self-reported

discovery

diverges

from

what

they

actually

did

by

roughly

half.
 • Answers arrive after the window closes. Fielding a fresh study takes weeks, long after the
premiere

moment,

and

the

chance

to

act

on

it,

has

passed.

Why last-click attribution is close to useless
The industry's default answer is last-click attribution: credit whatever the viewer touched immediately
before

tune-in,

which

is

almost

always

a

branded

search

or

a

direct

app

open.

That

number

tells

you

very

little.

By

the

time

someone

types

a

show's

name

into

Google

and

clicks,

the

decision

to

watch

has

already

been

made.

The

search

is

a

receipt,

not

a

cause.

Crediting

it

rewards

the

channel

that

happened

to

be

standing

at

the

door,

and

tells

you

nothing

about

what

actually

changed

the

viewer's

mind.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 4 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 03 · THE SOLUTION

How Meridian Works
Meridian is the software, not the panel. It is a lightweight, opt-in companion app that recruited
viewers

choose

to

run,

theirs

or

a

research

partner's.

Participants

stay

in

control;

teams

receive

structured,

cross-platform

behaviour

around

their

titles,

never

raw

screenshots

and

never

scraping.

Capture

and

redaction

run

on-device
,

and

personal

identifiers

are

stripped

before

anything

is

stored.

The

flow

is

three

deliberate

stages:

01 Capture the journey When a panelist begins anything show-related, whether streaming an episode, searching a trailer, scrolling fan edits, reading a recap, or buying merchandise, they press Start, and Meridian reads what is on screen during that window only. Nothing is captured in between. Capture and redaction run locally; personal details are removed before anything leaves the device.

02 Map the cohort Screen activity across apps, sites, video and conversation is resolved into structured signals: what was watched, the searches and social posts that led there, time on each platform, sentiment, shopping, and where one journey hands off to the next. Everything is rolled up across the whole cohort, comparable across titles and segments, not a single anecdote.

03 Act on it Dashboards, cohorts, funnels and AI-written daily syntheses turn the map into decisions: where to place promos for a new season, which platforms drive tune-in, what to greenlight, and how a title travels from premiere to group chat, answered against history instantly.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 5 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 04 · ARCHITECTURE

Inside the Companion App: Capture & Privacy
Architecture

Meridian's data comes from a native desktop companion app that participants install and run
themselves.

The

app

is

built

on

Tauri,

a

Rust

core

with

a

web

interface,

and

embeds

a

local

engine

that

performs

all

capture

and

processing

on

the

participant's

own

machine.

Only

when

a

journey

ends,

and

only

a

curated

subset,

is

anything

sent

to

the

cloud.

The

diagram

below

shows

the

full

path,

from

a

consented

screen

to

the

dashboard.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 6 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL

 Figure. Capture, processing and redaction run on the participant's device. A sampled, scrubbed subset is uploaded at end
of

journey

to

a

secure

per-participant

database,

which

feeds

the

Meridian

dashboard.

Five principles shape the architecture:
• Consent-gated. Nothing is captured outside an explicit, participant-initiated window. • Local-first. Capture, OCR and transcription all run on-device, and raw media never leaves the
machine.
 • Speaker-audio only. The microphone is never recorded, and this is enforced in code rather
than

policy.
 • DRM-aware. Protected streaming content is detected and skipped before any frame is taken.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 7 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 • Selective egress. Only a sampled, structured subset is uploaded, and only when a journey
ends.

The consent model: journey windows
All capture sits behind a single switch the participant controls, called a journey. Recording happens
only

between

pressing

Start

and

End.

Outside

that

window

the

engine

writes

nothing,

whether

or

not

the

app

is

open.

The

control

is

mirrored

to

the

home

screen,

a

menu-bar

tray

and

a

floating

pill,

and

it

survives

a

restart,

so

an

in-progress

session

is

recovered

rather

than

recorded

silently.

There

is

no

always-on

background

recording:

capture

is

a

discrete,

visible,

participant-driven

act.

What the engine captures, on-device
Screen. Screen frames are captured through Apple's ScreenCaptureKit on an event-driven cadence,
on

an

app

switch,

a

click,

a

pause

in

typing

or

a

settled

scroll,

rather

than

a

constant

frame

rate,

which

records

meaningful

state

changes

without

wasting

battery.

Before

any

frame

is

taken,

a

pre-capture

check

uses

the

macOS

accessibility

tree

and

the

window

list

to

detect

protected

(DRM)

content

in

native

apps

and

browser

tabs;

when

protected

content

is

in

focus,

capture

pauses

and

resumes

the

instant

the

participant

switches

away.

Text

is

read

entirely

on-device,

first

from

the

accessibility

tree

and,

where

that

is

thin,

with

Apple

Vision

OCR.

No

cloud

service

is

used

for

text

extraction.

Audio. Only system (speaker) audio is captured, never the microphone. Device selection uses the
default

output

device,

and

an

explicit

guard

rejects

any

input

device

even

if

one

is

configured,

so

a

manual

settings

change

cannot

re-enable

microphone

capture.

Speaker

audio

is

transcribed

locally

with

Whisper

to

confirm

which

title

or

episode

is

playing.

Raw

audio

files

are

never

uploaded.

Browser. A lightweight Chromium extension complements screen capture where DRM and native
rendering

make

screen

pixels

unreliable.

It

connects

to

the

local

engine

over

a

loopback

WebSocket

and

reports

structured

media-playback

state

roughly

every

ten

seconds,

including

page,

title,

position,

duration

and

mute

state,

which

is

what

reconstructs

which

title

was

watched

and

for

how

long.

It

captures

at

most

one

non-DRM

video

frame

every

thirty

seconds,

and

a

brightness

check

drops

DRM-blocked

black

frames

so

protected

content

is

never

stored.

Browser

frames

and

media

snapshots

are

pruned

on

a

seven-day

rolling

local

window.

Privacy by construction: PII redaction
A dedicated redaction layer scrubs personal data before it is stored or sent. Around two dozen
detectors

cover

emails,

phone

numbers,

IP

addresses,

payment

cards,

government

identifiers,

API

keys

and

secrets,

private

keys,

passwords

and

recovery

phrases;

each

match

is

replaced

with

a

typed

placeholder

such

as

[EMAIL]

or

[SSN].

For

study

builds

the

layer

is

enabled,

so

audio

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 8 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 transcripts are redacted before they are persisted, and extracted screen text is scrubbed on egress
with

bounding

boxes

preserved.

Where the data lives, and what reaches the cloud
By default, the heavy material stays on the participant's machine: raw audio, the full local frame and
text

history,

and

accessibility

detail.

When

a

journey

ends,

and

only

then,

a

curated

subset

is

uploaded

to

a

secure

cloud

database:

a

sampled

set

of

journey

frames,

roughly

one

every

five

seconds

within

the

window,

and

the

derived

structured

signals,

such

as

what

was

watched

and

time

on

each

platform.

Every

cloud

write

is

tied

to

the

authenticated

participant

and

isolated

per

person

by

row-level

security;

anything

captured

before

sign-in

is

excluded.

From

that

database,

the

signals

surface

in

the

Meridian

dashboard

shown

throughout

this

document.

PERMISSION
 WHY IT IS NEEDED
 WHAT IT DOES NOT DO

Screen Recording
Capture screen frames during a journey
No capture outside Start and End; DRM content is skipped
Microphone
Required by macOS to reach the audio subsystem for speaker audio
Microphone input is never read or transcribed; enforced in code
Accessibility
Read structured on-screen text and detect the active app and DRM
Used for text extraction and DRM gating, not content keystroke logging Additional hardening: the engine binds to the loopback interface only, the browser bridge accepts a
single

connection

chosen

during

onboarding,

and

untrusted

page

titles

and

URLs

are

written

with

bound

parameters.

Participants

can

pause

at

any

time

and

delete

a

journey

from

their

own

machine;

deleting

locally

is

designed

to

leave

the

study's

uploaded

copy

intact.

 05 · METHODOLOGY

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 9 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL

Methodology & the Demonstration Panel
To exercise the platform on a realistic portfolio, Prometheus Innovations modeled a Meridian
demonstration

panel

across

the

Paramount

slate.

The

panel

was

designed

to

span

genres,

across

unscripted,

scripted,

animation

and

daytime,

so

the

data

reflects

the

full

breadth

of

a

real

network

portfolio

rather

than

a

single

hit.

All

participants,

sessions

and

figures

shown

are

synthetic.

Participants opt in and run the Meridian companion app. Each show-related episode of activity is
bounded

by

an

explicit

Start

and

End

window;

between

windows,

nothing

is

captured.

Within

each

window,

on-device

processing

resolves

screen

activity

into

structured

signal

and

strips

personal

identifiers

before

storage.

Those

signals

are

then

rolled

up

across

the

cohort

into

the

dashboard

views

shown

throughout

this

document.

 Figure. The Meridian engagement dashboard for the demonstration panel: participant mix by show, session volume, and
attention

time

at

a

glance.

(Mock

data.)

 The panel at a glance
Forty-one participants were enrolled across eleven shows. The mix below reflects the demonstration
cohort

that

produced

the

journey,

engagement

and

conversation

data

in

Section

06.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 10 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL

SHOW
 GENRE
 PARTICIPANTS

SHARE OF PANEL

Survivor Unscripted / competition 10 24%
Big Brother Unscripted / competition 8 20%
NCIS Scripted drama 6 15%
South Park Animation / comedy 5 12%
Star Trek Scripted genre 5 12%
The Real Housewives Unscripted / reality 4 10%
Tyler Perry's Sistas Scripted drama 1 2%
Beyond the Gates Daytime drama 1 2%
The Bold and the Beautiful Daytime drama 1 2% Across the captured window the panel produced 146 cross-platform sessions from 28 active
participants
,

totalling

6

hours

23

minutes

of

attention-verified

activity.

Every

minute

is

tied

to

a

participant

and

the

platform

it

actually

happened

on,

deduplicated

to

distinct

people

and

content.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 11 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 06 · WHAT THE DATA REVEALED

The Cross-Platform Path to Tune-In
Meridian aligns every panelist's journey at their first show-watching moment, so the entry column
shows

where

viewing

started

and

each

band

shows

where

audiences

moved

next.

For

the

demonstration

cohort,

the

picture

was

unmistakably

multi-platform:

discovery

rarely

began

and

ended

in

one

place.

Journeys

relayed

between

video,

search,

social

and

the

destination

app,

exactly

the

route

first-party

analytics

cannot

see,

and

exactly

the

upstream

steps

that

last-click

attribution

throws

away.

 Figure. Cohort Journey Flow. Entry points fan out across YouTube, Reddit, Google, social and the destination app before
and

after

tune-in.

Band

width

equals

users;

colour

follows

platform.

(Mock

data.)

Journeys entered through YouTube (the single largest entry point), Google search, the destination
streaming

app

itself,

and

Meridian's

own

recruitment

link,

then

handed

off

repeatedly

between

Reddit,

Facebook,

Instagram,

X

and

back

to

YouTube
.

Several

paths

ran

straight

through

search

results

into

the

streaming

app

and

the

show's

merch

store,

capturing

the

full

arc

from

curiosity

to

viewing

to

purchase.

The

click

that

a

last-click

model

would

credit

sits

at

the

very

end

of

these

chains;

Meridian

recorded

everything

before

it.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 12 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL

 Where attention actually went
Beyond the path, Meridian resolves how each panelist spent their show-related time and which
platforms

carried

that

attention.

For

the

demonstration

cohort,

short-form

clips

dominated

consumption,

with

a

meaningful

tail

of

shopping

behaviour,

a

signal

first-party

player

analytics

would

never

surface.

 Figure. Engagement mix and platform usage. Clips drove the majority of observed minutes; YouTube was the most-used
surface,

followed

by

Google

Search,

Facebook

and

Reddit.

(Mock

data.)

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 13 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL

 Engagement mix
ACTIVITY TYPE

SHARE OF OBSERVED MINUTES

READ

Clips 69%
Short-form video dominated the cohort's time.
Shopping 21%
One in five observed minutes carried commercial intent.
Reading 6% Recaps, articles and threads.
Discussion 4% Active posting and commenting.
Full-episode watching 0% No long-form watching in this window. The takeaway for programming and marketing is concrete: for these titles, the cohort lived in clips
and

conversation
,

not

long-form,

and

one

in

five

observed

minutes

carried

commercial

intent.

That

is

precisely

the

kind

of

cross-surface

insight

that

reframes

where

promo

and

commerce

dollars

should

sit,

and

which

first-party

player

telemetry

cannot

produce.

Attention-verified completion
Player-open is not the same as watched. Meridian measures how much of each video viewers
actually

watched

from

playback

telemetry,

and

flags

muted

or

backgrounded

playback

so

completion

reflects

genuine

attention

rather

than

an

open

tab.

This

keeps

reporting

honest:

a

view

with

the

sound

off

and

the

tab

in

the

background

is

not

the

same

asset

performance

as

a

focused,

audible

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 14 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 watch.

 Figure. Episode completion is attention-verified. Bars reflect real watched time, with badges flagging muted or
backgrounded

playback.

(Mock

data.)

In the demonstration, a full-episode upload reached roughly 27% completion but ran muted ; a
short

auction

clip

on

the

destination

app

played

in

the

foreground

to

about

17%
.

Surfacing

these

badges

lets

ad-sales

and

marketing

report

completion

as

attention,

not

player-open

time,

the

difference

between

a

number

a

buyer

trusts

and

one

they

discount.

Fan attention & conversation
Platforms report likes; only the panel sees what fans actually scrolled past, opened, and talked
about.

Meridian

ties

social

behaviour

to

consenting

viewers,

never

scraping

strangers,

and

resolves

it

into

topics,

sentiment

and

the

exact

language

fans

use

about

a

title.

 Figure. Fan attention. The attention ladder from feed impression to like, set against public traction, for a single observed
post.

(Mock

data.)

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 15 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 The same logic scales from a single post to the whole conversation. Across the cohort, Meridian
classified

every

post

that

appeared

in

fans'

feeds

into

topics,

tone

and

engagement,

separating

what

fans

merely

saw

from

what

they

chose

to

act

on.

 Figure. Content summary. The cohort logged 86 interactions across 67 posts from 46 authors, led by Sistas, TV and Big
Brother

conversation.

(Mock

data.)

 What the conversation showed
SIGNAL
 DEMONSTRATION RESULT

Posts seen in fans' feeds 67 across 46 distinct authors
Liked by panelists 19
Commented / shared 1 / 0
Tone of content consumed 38% neutral, 31% positive, 17% mixed, 14% negative
Tone of participant reactions 100% positive
Most-discussed titles Sistas (28), TV (15), Big Brother (9)

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 16 of 17

 PROMETHEUS INNOVATIONS · Meridian
 CONFIDENTIAL
 This is the attention ladder in miniature: seen, opened, liked, talked about , deduplicated to distinct
posts

and

people,

so

marketing

receives

the

actual

words

fans

use

about

a

title,

ready

to

brief

the

next

campaign

rather

than

guess

at

it.

07 · THE PLATFORM

The Meridian Platform
One panel produces the whole picture of an audience's media day, not just the minutes inside a
single

app.

The

demonstration

exercised

the

full

Meridian

capability

set:

CAPABILITY
 WHAT IT DELIVERS

Cross-platform attention share
Where viewing time actually goes, your titles against every other streamer, network and video surface, unified into one share, so you see who you are really competing with for the night.
Discovery & tune-in paths
The exact route to a premiere: the trailer, the edit, the recap, the friend's text or the search that drove someone to press play, so you know which channels convert to tune-in.
What they watch & say
On-device transcription turns what audiences watch and discuss into topics, sentiment and the exact words fans use, privately, with personal identifiers removed.
Fan cohorts & the attention ladder
Seen, engaged, liked, talked about. Track how viewers climb from curious to superfan and compare cohorts: new against lapsed, one title against the whole slate.
First-party social signal
Likes, comments, shares and saves on your trailers, clips and episodes, tied to consenting viewers, so you see which assets move a known, opted-in audience.
Daily AI synthesis
During a launch window, agentic analysis writes a plain-language read of what moved each day, KPIs first, evidence attached, so teams act while the premiere is still live.

Paramount × Meridian, Case Study (illustrative)
 © 2026 Prometheus Innovations, Inc.
 Page 17 of 17
