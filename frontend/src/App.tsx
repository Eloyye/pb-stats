import { useEffect, useState, type FormEvent } from "react";
import {
  fetchWorkspace,
  patchWorkspace,
  readWorkspace,
  sessionHeaders,
  type Workspace,
} from "./api";

export function App({ sessionToken }: { sessionToken: string }) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [name, setName] = useState("");
  const [notice, setNotice] = useState("");
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    if (!sessionToken) return;
    void fetch("/api/workspace", {
      headers: sessionHeaders(sessionToken),
      signal: controller.signal,
    })
      .then(readWorkspace)
      .then((current) => {
        setWorkspace(current);
        setName(current.name);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted)
          setError(
            reason instanceof Error
              ? reason.message
              : "Unable to load workspace.",
          );
      });
    return () => controller.abort();
  }, [sessionToken]);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const outcome = await patchWorkspace(
        sessionToken,
        name.trim(),
        workspace.revision,
      );
      if (outcome.kind === "conflict") {
        setConflict(true);
        setNotice(
          "Workspace changed. Your unsaved name is preserved. Review the latest saved name below, then retry to apply your change.",
        );
        if (outcome.currentRevision !== null) {
          const currentRevision = outcome.currentRevision;
          setWorkspace((current) =>
            current ? { ...current, revision: currentRevision } : current,
          );
        }
        try {
          setWorkspace(await fetchWorkspace(sessionToken));
        } catch {
          // The 409 payload already advanced the revision above, so a retry
          // still targets the latest revision even when this refetch fails.
          setError(
            "Workspace changed, but the latest saved name could not be loaded. Retry to apply your change with the latest revision.",
          );
        }
      } else {
        setWorkspace(outcome.workspace);
        setName(outcome.workspace.name);
        setConflict(false);
        setNotice("Match name saved.");
      }
    } catch (reason: unknown) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to save. Your unsaved name is preserved.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <p className="eyebrow">Local workspace</p>
      <h1>Pickleball Match Analysis</h1>
      <p>Review match evidence and preserve operator corrections.</p>
      {!sessionToken ? (
        <p role="alert">
          Open the session link printed by the coordinator to connect.
        </p>
      ) : (
        <>
          {error && <p role="alert">{error}</p>}
          {notice && (
            <p role="status" className={conflict ? "conflict" : ""}>
              {notice}
            </p>
          )}
          {workspace ? (
            <section aria-labelledby="match-heading">
              <h2 id="match-heading">Match workspace</h2>
              <p>
                Saved name: <strong>{workspace.name}</strong>
              </p>
              <p>Revision {workspace.revision}</p>
              <form
                onSubmit={(event) => {
                  void save(event);
                }}
              >
                <label htmlFor="match-name">Match name</label>
                <input
                  id="match-name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  disabled={busy}
                  required
                  maxLength={120}
                />
                <button type="submit" disabled={busy || !name.trim()}>
                  {busy ? "Saving…" : conflict ? "Retry save" : "Save name"}
                </button>
              </form>
            </section>
          ) : (
            !error && <p role="status">Loading workspace…</p>
          )}
        </>
      )}
    </main>
  );
}
