# Pickleball Statistics

A personal project for pickleball statistics enthusiasts: analyze professional doubles footage to understand **where players and teams lose rallies, with video evidence supporting the statistics**.

This README describes the agreed v1 plan, not implemented capabilities. Canonical domain terms are defined in [CONTEXT.md](CONTEXT.md).

The [V1 architecture and UI design](docs/v1-design.md) records the detailed workflow, data model, processing design, and implementation milestones. The [quality checks](docs/quality.md) document the implemented uv, Ruff, and ty tooling and remaining validation work.

## V1 scope

- Process one complete doubles match at a time from a supported broadcast format.
- Start from a local video file and record its source URL. Keep annotation and playback timestamps tied to that file.
- Run locally on Windows 11 with an NVIDIA RTX 5080 and 32 GB system RAM. Processing speed and resource use must be benchmarked on that machine.
- Provide a local dashboard for import, setup, processing progress, rally review, and reporting, with saved progress and resumption between sessions.
- Target **15 minutes of operator setup and review per hour of footage**. This is a target to demonstrate, not an established capability. Overnight processing is acceptable initially.
- Permit incomplete reports when evidence cannot resolve every event, with explicit coverage and exclusions for each metric.

### Initial footage

The provisional source family is the official PPA Tour's Carvana Mesa Cup broadcasts, beginning with [Johns/Tardio vs Patriquin/Alshon at the The Carvana Mesa Cup](https://www.youtube.com/watch?v=Vzny7HAc7cA). PPA's [event statistics](https://www.ppatour.com/championship-sunday-standout-stats-from-the-carvana-mesa-cup-2/) provide independent game-score and rally-statistic cross-checks.

The video listing and published results have been checked. Playback availability, completeness, image quality, scoreboard layout, camera changes, replays, and audio quality still need inspection before this becomes a validated input format. Select a separate match from the same source family for held-out evaluation, including at least one complete manually checked game.

Supporting this format includes handling its camera cuts, broadcast transitions, replays, and occlusions. It does not imply support for arbitrary YouTube broadcasts.

## Operator workflow

1. **Import:** select a local video file and record its source URL.
2. **Set up:** identify all four players and their teams, confirm the scoring format, and confirm or correct court landmarks when necessary. This time counts toward the review budget.
3. **Process:** identify live rallies and shots, carry player identities through camera cuts and side changes, estimate coarse court regions, and reconstruct rally-boundary score states.
4. **Review:** work through a queue organized by rally and prioritized by its effect on the report. Each item shows the clip, proposed labels, and reason for review. Accept, correct, or leave labels unknown; any rally remains available for inspection outside the queue.
5. **Report and export:** browse the match statistics and supporting clips, with CSV/JSON exports of statistics and corrected annotations.

## First report

- A rally browser with video timestamps and player/team attribution where known.
- Player/team rally outcomes, kept distinct from scoring points: winning a rally does not always add a point under side-out scoring.
- Shot-type counts, with contact mode and rally role recorded separately.
- Serve, return, and third-shot net-or-out error rates by player/team where attribution is known.
- Numerators, denominators, and excluded/unknown counts alongside percentages, with coverage visible for each metric.

### Shot labels

Record these as separate attributes rather than competing labels:

| Attribute | Initial values |
| --- | --- |
| Shot type | Dink, drop, dropshot, drive, lob, overhead, block/reset, other, unknown |
| Contact mode | Volley, after bounce, unknown |
| Rally role | Serve, return, third shot, later shot with sequence number where known, unknown |

A volley dink can therefore retain both its shot type and its contact mode. A known hitter or rally role does not require a known shot type.

Use **other** when the observed shot falls outside the named categories and **unknown** when the evidence is insufficient to classify it. Keep these values separate in annotations and reports.

The agreed annotation convention distinguishes three soft shots:

- **Drop:** a shot from the baseline or transition area intended to land softly near the opponent's net/kitchen area.
- **Dink:** a soft kitchen-line exchange against opponents positioned at the kitchen.
- **Dropshot:** a soft shot from the kitchen line placed near the net against an opponent positioned farther back.

These labels require coarse positioning even though positioning analytics are deferred. The annotation guide must supply examples and boundary cases; use unknown when the evidence cannot support a distinction.

### Error rates

For each rally role (serve, return, or third shot):

```text
error rate = attempts ending in the net or out / attempts with known immediate outcomes
```

Count only failure on the shot itself. A third shot that lands in and is then attacked is not an error under this metric, even if its team loses the rally. Record other faults separately.

An attempt needs known rally role and immediate outcome to enter that role's rate, and known attribution to enter a player/team breakdown. Show relevant exclusions separately. A zero denominator yields an unavailable rate, not 0%.

These rates measure observed net/out failures, not shot quality. Missing observations may be systematic, so rates over known attempts must not be presented as complete-match rates without their coverage.

Show eligible versus detected attempts and unresolved observation gaps. If additional attempts may be missing and their count is unknown, detected-attempt coverage must not be presented as complete-match coverage.

## Evidence and uncertainty

### Partial observations

Preserve each supported fact independently. An occluded contact may leave the hitter or shot type unknown without invalidating a known rally outcome. Conversely, an uncertain score does not erase independently known shot facts.

Exclude an unknown attribute only from metrics that require it. Missing evidence must not become a successful attempt, a non-error, or an invented shot. If a gap makes shot order uncertain, retain that uncertainty in rally-role labels.

### Player identity and court regions

The operator establishes player identities and team membership. Carry those identities through camera changes and side changes, requesting correction when identity is uncertain.

V1 needs coarse baseline, transition, and kitchen-line regions, not complete physical reconstruction. Use visible court geometry and known court dimensions where supported, with operator correction of landmarks when needed. Re-establish the mapping after camera changes. When an angle or occlusion prevents a reliable mapping, leave dependent position and shot labels unknown.

### Replays and transitions

Detect and exclude replay sequences from automatic event counting so a replayed shot cannot create another rally or attempt. Exclude broadcast transitions from live play as well. Operators may consult replay footage during review, but automatic recovery of missing live-shot information from replays is deferred. Preserve gaps in incomplete live sequences.

### Score state

Support side-out doubles with an operator-confirmed target of **11, 15, or 21, winning by two**, including the opening service-turn exception and initial 0–0–2 score call. Track at each rally boundary:

- Both teams' scores.
- Serving team and serving player.
- Server number, 1 or 2, within the current service turn.

Use **service turn** and **server number**, rather than possession and outs. Server number is not a permanent player identity. The scoring model follows the [official side-out rules](https://usapickleball.org/rules/summary/) and [scoring explanation](https://usapickleball.org/strategies/pickleball-scoring-positioning-side-out-scoring/).

Combine audio announcements, scoreboard overlays, and inferred rally outcomes as evidence. No source is universally authoritative. Check transitions against the rules, accommodate delayed overlays, and send unresolved conflicts to review. Corrections update subsequent dependent states until the next confirmed checkpoint; conflicting checkpoints require review.

### Corrections and reuse

Save the original prediction, operator correction, video timestamp, and model version. Corrections update dependent states and statistics immediately and remain available across sessions and reprocessing. Preserve reusable annotations for future model improvement.

Saving corrections does not trigger automatic training. Evaluate future model changes against the held-out benchmark before adopting them.

## Development sequence and validation

1. **Inspect footage and define annotations.** Validate the proposed source format, inspect representative segments, and write a short annotation guide with examples and ambiguous cases.
2. **Build the review foundation.** Implement enough of the rally browser and correction interface to create reference annotations for rally boundaries, identities, shot labels, and outcomes. Benchmark preparation is separate from the routine 15-minute review target.
3. **Benchmark a minimal local pipeline.** Start with representative segments on the Windows processing machine before attempting full matches. After the first pilot, set numerical accuracy and coverage targets before expanding development.
4. **Add reports and evaluate held-out footage.** Use a separate match from the same source family, with at least one complete manually checked game kept out of tuning. Measure accuracy and coverage by category, processing time, and total operator setup/review time; distinguish automatic output from corrected output.

The first useful workflow must connect reported statistics to inspectable footage, retain uncertainty and corrections, and be evaluated against manually checked evidence. Game totals alone are insufficient to validate shot labels or attribution.

If the workflow misses the review-time target, explicitly revisit the weakest feature or the supported-footage boundary before expanding scope. Do not hide the failure by silently dropping difficult observations or relaxing the target. Model choices and numerical accuracy/coverage thresholds remain pilot decisions rather than assumed capabilities.

## Later milestones

After the single-match workflow is validated:

- Shot-placement heatmaps, including overall and shot-sequence ranges.
- Batch queueing and automatic YouTube ingestion.
- Broader broadcast-format support and cloud processing options.
- Automatic use of replays to recover missing live-shot information.
- Automated retraining from reviewed annotations.
- Spin classification: topspin, sidespin, backspin, and flat.
- Continuous ball trajectories, detailed paddle/ground/player contact reconstruction, full 3D reconstruction, and estimated velocity with validated uncertainty intervals.
- Positioning analytics and court-coverage heatmaps, including baseline and kitchen coverage.
- Kitchen-establishment metrics, kitchen unestablished error percentage (KUEP), return-hold percentage, and dink error percentage. Define their events, populations, and denominators before implementation; no complement relationship between return-hold and KUEP is assumed.

## Development setup

Python tooling uses uv, Ruff, and ty with strict annotation and type-checking rules. After installing uv, run:

```bash
uv sync --locked --dev
uv run --locked python scripts/check_quality.py
```

These commands check the tooling foundation; the application and model pipeline are not implemented yet. See [quality checks](docs/quality.md) for local/CI behavior and the test requirements for the first application slice.

For agentic development:

- Prerequisite: `npx` must be available through the npm installation.
- Run this command to access skills:

```bash
npx skills i
```
