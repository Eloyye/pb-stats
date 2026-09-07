# Annotation guide

Version: `0.1-draft`. Status: awaiting footage examples and operator agreement; **not frozen for benchmark annotation**. This is the proposed contract for [issue #9](https://github.com/Eloyye/pb-stats/issues/9). [Issue #23](https://github.com/Eloyye/pb-stats/issues/23) owns the pilot reference and complete-game annotations. The [validation record](validation.md) tracks the footage and remaining gates.

Use the vocabulary in [CONTEXT.md](../../CONTEXT.md). The examples below are illustrative labeling cases, not observations of the proposed videos. Replace or supplement them with source-anchored examples before freezing this guide.

## Evidence and boundaries

Annotate the identified local source file. Record its content digest, indexed source frame or source presentation timestamp/time base, and a readable time. A YouTube seek time alone is not a reusable local-file anchor. Never silently reuse anchors for a different encode. Keep the original prediction, human decision, reason, reviewer, date, and guide version with each revision.

A rally begins with the serve attempt and ends when play stops and its outcome is established. Mark the serve contact and end-of-play evidence where visible; retain an uncertain boundary interval when an exact frame is unavailable. A failed serve remains a rally and an attempt. Game boundaries need opening and final-state evidence; a title card alone does not establish completeness.

Create one shot per supported live attempt. Record contacts, hitters, team, shot type, contact mode, rally role, immediate outcome, and rally outcome independently. Do not create guessed contacts to bridge missing footage. Record an observation gap with its source interval, affected attributes, and missing-attempt count if known; otherwise leave that count unknown. Roles beyond a gap remain unknown unless independent evidence resolves the sequence.

Identify players through operator-confirmed names and teams, never by server number or a permanent near/far screen position. After a camera or side change, reassess identities and court landmarks. Record baseline, transition, or kitchen-line position only when geometry supports it. Ambiguous region boundaries remain unknown; this draft does not impose unvalidated distance thresholds.

## Independent shot attributes

| Attribute | Values and rule |
| --- | --- |
| Shot type | Dink, drop, dropshot, drive, lob, overhead, block/reset, other, unknown |
| Contact mode | Volley, after bounce, unknown; do not infer from shot type |
| Rally role | Serve, return, third shot, later shot with sequence number where known, unknown |
| Immediate outcome | In, net, out, other fault, unknown; annotate what happened on this attempt |
| Hitter / team | Resolve each attribution only as far as supported; a known team need not imply a known hitter |
| Rally outcome | Winning team or unknown; separate from whether a scoring point is awarded |

The following soft-shot distinctions are the project convention. Infer the intended soft placement only when the trajectory and positions support it; a failed attempt may retain a known type. Do not decide type from whether the rally was won.

| Illustrative case | Label and boundary |
| --- | --- |
| Hitter at baseline or in transition sends a soft arc toward the opponent's kitchen | **Drop**; it need not be the third shot and need not succeed |
| Players exchange soft shots at the kitchen line with opponents at the kitchen | **Dink**; record volley or after bounce separately |
| Kitchen-line hitter softly places the ball near the net while the relevant opponent is farther back | **Dropshot**; distinguish from a dink using the opponent's visible position |
| Soft third shot from baseline catches the net | **Drop**, third shot, net if each fact is visible; failed placement does not change the type |
| Soft kitchen-line shot, but opponent position is hidden or mixed positioning makes the pattern unclear | **Unknown** type with a position-ambiguity reason; retain known contact mode or role |
| Contact clearly belongs to play, but trajectory or camera geometry is hidden | **Unknown**, not other; preserve independently known hitter/outcome |

For the remaining types, use these draft descriptions consistently: **drive** is a forceful forward attacking shot; **lob** follows a high arc intended over opponents; **overhead** uses an overhead striking motion; **block/reset** absorbs or redirects an incoming attack defensively. If multiple categories fit and evidence does not resolve the play pattern, use unknown and flag the boundary case for the pilot guide review. These descriptions also need observed examples before the guide is frozen.

Use **other** only when the observed play pattern is clear and outside the named categories, and write what was observed. For example, an observed serve may have a known role and contact mode while its type is other if it fits none of the named patterns. Do not label all serves other automatically. Use **unknown** when classification evidence is insufficient; write the missing evidence rather than guessing. An unresolved overlap between categories is unknown, not other.

## Replay, transition, and outcome cases

| Illustrative case | Annotation action |
| --- | --- |
| Broadcast repeats an earlier winner from a different angle | Mark replay span; create no additional rally or attempt |
| Replay or transition covers the return to live play | Exclude the replay/transition and preserve the missing live interval as a gap |
| It is unclear whether a clip is replay or live | Mark classification unresolved for review; do not silently count it as live |
| Operator consults replay to resolve a live shot | Link replay evidence to the existing live event and record a human decision; no automatic recovery and no duplicate event |
| Third shot lands in; opponent attacks it and wins | Immediate outcome in; not a third-shot net-or-out error |
| Foot fault with otherwise visible ball trajectory | Record other fault separately; do not turn it into a net/out failure |
| Ball leaves the picture and the next overlay changes | Immediate outcome unknown unless other evidence resolves it; score change alone does not prove net or out |

At rally boundaries, record both team scores, serving team/player, and server number independently. Confirm the game target and side-out format. Preserve opening server number 2, delayed overlays, audio/overlay disagreements, and uncertain states as evidence or review items. A conflicting score does not erase known shot facts. Apply corrections through dependent states to the next confirmed checkpoint and retain history as required by the [correction ADR](../adr/0001-preserve-corrections-through-reprocessing.md).

Role-specific net-or-out rates use attempts with known role and immediate outcome; net/out failures form the numerator. Other faults remain separately visible. Player/team breakdowns additionally need their attribution. Unknown shot type alone does not exclude an attempt. Show unknown-role attempts, excluded-event counts, overlapping missing-attribute reasons, and gaps; a zero denominator is unavailable. Unknown missing-attempt counts prevent complete-match coverage claims.

## Freeze procedure

1. Inspect representative pilot footage using the [validation record](validation.md), including difficult and ambiguous cases.
2. Add source-file/frame anchors for drop, dink, dropshot, other, unknown, replay exclusion, and category overlaps. Explain why the nearest alternative does not fit. If an example is absent, record the search extent and leave the unsupported distinction pending rather than inventing one.
3. Have the operator resolve or explicitly retain each boundary ambiguity. Record reviewer, date, source identities, agreed version, and any remaining unknown policy below.
4. Freeze a version before #23 creates benchmark references. Later semantic changes require a new version and explicit review of affected references; do not relabel the held-out set to favor a model result.

| Freeze field | Value |
| --- | --- |
| Frozen version / repository revision | Pending |
| Reviewer and date | Pending |
| Source-anchored examples | Pending; illustrative cases only |
| Open boundary decisions | Coarse-region ambiguity and drive/lob/overhead/block-reset overlaps to check against pilot footage |
| Ready for #23 reference annotation | No |
