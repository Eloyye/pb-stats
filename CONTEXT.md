# Pickleball Match Analysis

Vocabulary for describing doubles pickleball rallies, shots, scoring, and the evidence supporting match statistics.

## Language

### Match and scoring

**Rally**:
A passage of play beginning with a serve attempt and ending when play is stopped and a rally outcome is determined.

**Rally outcome**:
The team that wins or loses a rally, distinct from whether a scoring point is awarded.

**Service turn**:
A team's opportunity to serve until a side-out transfers service to its opponent.
_Avoid_: Possession

**Server number**:
The first or second server within a team's current service turn, as used in the score call; the opening service turn begins with server number 2. It is not a permanent identity assigned to a player.
_Avoid_: Outs

**Side-out**:
The transfer of service from one team to the other after the serving team's service turn ends.

### Shot attributes

**Shot type**:
The classification of a shot's play pattern, such as dink, drop, dropshot, drive, lob, overhead, or block/reset, separate from contact mode and rally role.

**Other shot type**:
A shot whose observed play pattern falls outside the named shot-type categories. It is distinct from an unknown shot type, for which the evidence is insufficient to classify the shot.

**Contact mode**:
Whether a shot is struck as a volley or after a bounce.

**Rally role**:
A shot's place in the rally sequence: serve, return, third shot, or a later shot.

**Drop**:
A shot from the baseline or transition area intended to land softly near the opponent's net/kitchen area.

**Dink**:
A soft kitchen-line exchange against opponents positioned at the kitchen.

**Dropshot**:
A soft shot from the kitchen line placed near the net against an opponent positioned farther back.

**Net-or-out error**:
A shot attempt that itself ends in the net or out of bounds, independent of subsequent rally results. Other faults and poor-quality shots that land in are not net-or-out errors.

### Analysis evidence

**Unknown**:
An attribute for which the available evidence does not support a resolved value; other attributes of the same shot or rally may still be known.

**Metric coverage**:
The extent to which relevant observations have sufficient known attributes to contribute to a particular metric, with exclusions made explicit.

**Detected-attempt coverage**:
The proportion of detected shot attempts with sufficient known attributes to contribute to a particular metric. It does not establish complete-match coverage when additional attempts may be missing.

**Observation gap**:
A span of play in which the available evidence does not establish a complete sequence of events. The number of missing shot attempts may itself be unknown.

**Replay**:
A broadcast presentation of previously shown play, rather than another occurrence of its shots or rally.

**Operator correction**:
A human revision of an inferred match fact or label after reviewing the evidence.

**Automatic observation**:
A match fact or label inferred by a model without human confirmation. Its eligibility for a metric depends on validated acceptance rules and the attributes required by that metric.

**Operator confirmation**:
A human verification that an inferred match fact or label agrees with the available evidence, without changing its value.
