# Preserve corrections through reprocessing

Model reprocessing may change detected events, so human corrections must remain distinct from replaceable predictions and must never be silently overwritten. Reapply a correction only when its corresponding event is identified reliably; event splits introduced by reprocessing require review, and ambiguous correspondence must not silently transfer a correction to a different event. This adds reconciliation work but preserves reviewed evidence when models or event segmentation change.

While a reprocessed interpretation conflicts with the previous consistent interpretation, retain the previous one for reporting and visibly flag the pending conflict. Promote the replacement after reconciliation; when initial processing has no previous consistent interpretation, leave disputed facts unresolved.
