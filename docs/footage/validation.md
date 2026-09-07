# Footage validation and held-out reservation

Status: preparation for [issue #9](https://github.com/Eloyye/pb-stats/issues/9), with human visual validation pending. Updated 2026-09-06. The provisional family is official PPA Tour Carvana Mesa Cup doubles broadcasts. Event membership is a source-selection clue, not proof that production layout, camera behavior, or audio match.

## Source record

| Field | Pilot / development source | Held-out candidate |
| --- | --- | --- |
| Match | Ben Johns / Gabe Tardio vs Hayden Patriquin / Christian Alshon, men's doubles final | Anna Leigh Waters / Ben Johns vs Anna Bright / Hayden Patriquin, mixed doubles final |
| Event date | 2026-02-22, Carvana Mesa Cup | 2026-02-22, Carvana Mesa Cup |
| Video URL | [Vzny7HAc7cA](https://www.youtube.com/watch?v=Vzny7HAc7cA) | [4qSoA-jwpVM](https://www.youtube.com/watch?v=4qSoA-jwpVM) |
| Listing evidence | PPA Tour video listing identifies the men's final and publication date 2026-02-22 | [IntoPickleball listing](https://intopickleball.com/trending-matches/) associates this video ID with Waters/Johns vs Bright/Patriquin at the Carvana Mesa Cup; direct publisher verification pending |
| Published game scores, first team perspective | 8–11, 11–6, 11–8, 13–11 | 8–11, 9–11, 3–11 |
| Local file / content digest | Pending | Pending |
| Duration / video and audio stream metadata | Pending local inspection | Pending local inspection |
| Source timestamp origin / time base / frame index | Pending local indexing | Pending local indexing |
| Visual and audio inspection | Not performed | Not performed |
| Completeness / format validation | Unvalidated | Unvalidated |

The [official PPA event statistics](https://www.ppatour.com/championship-sunday-standout-stats-from-the-carvana-mesa-cup-2/) corroborate both matches and the scores above. Published totals are independent cross-checks, not frame-level annotations. Metadata and search listings were checked on 2026-09-06. Direct web fetching of the held-out YouTube page failed, so playback availability, publisher identity, and actual video contents remain unchecked. No source video or source timestamp observations are supplied by this record.

## Representative inspection record

Inspect the pilot first. For each row, append the local content digest, start/end source timestamps or frames, observed behavior, effect on annotation, reviewer, and date. Multiple observations may be needed for one category. Use pending, observed, or not found in an explicitly recorded search extent; an empty row is never a pass.

| Category | Evidence needed | Current result |
| --- | --- | --- |
| Completeness | Opening serve and final rally of every game; scan for removed live spans and compare game order/scores with published results | Pending |
| Ordinary live play | Representative early, middle, and late rallies; ball/contact/player visibility and court landmarks | Pending |
| Camera cuts and side changes | Each encountered view/layout; continuity of player identity and whether court mapping must be reset | Pending |
| Broadcast transitions | Entry/exit frames, whether transitions overlap or hide live play | Pending |
| Replays | Repeat-play cues and exact replay intervals; return-to-live behavior; duplicate-count risk | Pending |
| Occlusion | Hidden contacts or ball flight, affected attributes, known or unknown missing-attempt count | Pending |
| Scoreboard | Layout, legibility, score/server information, update lag, layout changes, and conflicts | Pending |
| Audio | Score calls and contact audibility; commentary/crowd interference, synchronization, missing audio | Pending |
| Annotation examples | Drop/dink/dropshot, other/unknown and overlaps in the [draft guide](annotation-guide.md), with explanatory frame anchors | Pending |

For each observed difficult span, record whether evidence supports a label, requires an unknown attribute/gap, or prevents the proposed footage scope. Do not discard difficult spans to make validation appear better. Set numerical accuracy and coverage targets after the pilot, as specified in the V1 design; this record does not invent thresholds.

## Held-out selection and tuning exclusion

Reserve the mixed doubles final above as the **held-out candidate**, with **game 1 provisionally designated** as the minimum complete-game reference. This selects a separate match at the same event while avoiding a different production year. It does not yet establish that the candidate meets the supported-format requirement. Shared players are permitted by the separate-match design; this is not a test of generalization to unseen players.

Keep the entire candidate match out of model fitting, prompt/rule/threshold selection, and development examples while it is reserved. Use the men's final for the representative inspection and guide examples. A human may inspect the reserved source to establish identity, completeness, and production compatibility and later create references; do not feed those annotations or performance results back into tuning.

Before accepting the reservation, verify the publisher and actual match, obtain the local source identity, confirm the same production family visually, and record game 1's opening-to-final-rally interval. A game is not complete merely because both score endpoints appear: record every rally and observation gap during #23's full-game annotation. If game 1 is incomplete, document that finding and the pre-evaluation reason for selecting another complete game or match. Do not replace it because a model scores poorly.

| Reservation / freeze field | Value |
| --- | --- |
| Candidate selected on | 2026-09-06 |
| Match reserved from tuning | `4qSoA-jwpVM`, pending identity/format verification |
| Minimum reference game | Game 1, pending completeness inspection and exact source interval |
| Prior tuning use checked by owner | Pending; no historical-use claim is made |
| Accepted source digest and game interval | Pending |
| Human selection confirmation / date | Pending |
| Frozen annotation-guide version | Pending |
| Full-game reference annotations | Not created; owned by #23 |

Freeze the accepted match identity, local source digest, complete-game interval, guide version, and owner/date before benchmark work. Record any previous development use; if this source has already informed tuning, nominate another match. Keep the frozen manifest with benchmark results, including model/configuration identity and the split used. Any future changes require a recorded reason and version.

## Remaining human handoff

The documentation is prepared, but #9 cannot yet close. The operator must supply or identify the two local source files, inspect representative pilot segments and the held-out compatibility/completeness gates, add actual timestamped examples, resolve draft label boundaries, and record the guide and held-out freeze. #23 then creates the pilot references and at least one complete manually checked held-out game using that frozen contract. Reference preparation time remains separate from the routine setup/review target.
