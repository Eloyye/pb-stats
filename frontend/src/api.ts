export type Workspace = { id: string; name: string; revision: number };

export type PatchOutcome =
  | { kind: "saved"; workspace: Workspace }
  | { kind: "conflict"; currentRevision: number | null };

export function sessionHeaders(sessionToken: string): Record<string, string> {
  return { "X-Session-Token": sessionToken };
}

export function isWorkspace(value: unknown): value is Workspace {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "string" &&
    "name" in value &&
    typeof value.name === "string" &&
    "revision" in value &&
    typeof value.revision === "number" &&
    Number.isInteger(value.revision)
  );
}

export async function readWorkspace(response: Response): Promise<Workspace> {
  if (!response.ok) throw new Error(`Request failed (${response.status}).`);
  const value: unknown = await response.json();
  if (!isWorkspace(value)) {
    throw new Error("The coordinator returned an invalid workspace.");
  }
  return value;
}

/** Extract the latest revision from a 409 conflict body; null when unparseable. */
export function readConflictRevision(value: unknown): number | null {
  if (typeof value !== "object" || value === null || !("detail" in value)) {
    return null;
  }
  const detail: unknown = value.detail;
  if (
    typeof detail !== "object" ||
    detail === null ||
    !("current_revision" in detail) ||
    typeof detail.current_revision !== "number" ||
    !Number.isInteger(detail.current_revision) ||
    detail.current_revision < 0
  ) {
    return null;
  }
  return detail.current_revision;
}

export async function fetchWorkspace(sessionToken: string): Promise<Workspace> {
  const response = await fetch("/api/workspace", {
    headers: sessionHeaders(sessionToken),
  });
  return readWorkspace(response);
}

export async function patchWorkspace(
  sessionToken: string,
  name: string,
  expectedRevision: number,
): Promise<PatchOutcome> {
  const response = await fetch("/api/workspace", {
    method: "PATCH",
    headers: {
      ...sessionHeaders(sessionToken),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, expected_revision: expectedRevision }),
  });
  if (response.status === 409) {
    let currentRevision: number | null = null;
    try {
      currentRevision = readConflictRevision(await response.json());
    } catch {
      currentRevision = null;
    }
    return { kind: "conflict", currentRevision };
  }
  return { kind: "saved", workspace: await readWorkspace(response) };
}
