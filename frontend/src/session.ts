const storageKey = "pb-stats-session";

// Session storage keeps the launch credential scoped to this browser tab.
export function takeSessionToken(): string {
  const token = new URLSearchParams(window.location.hash.slice(1)).get(
    "session",
  );
  window.history.replaceState(
    null,
    "",
    window.location.pathname + window.location.search,
  );
  try {
    if (token) window.sessionStorage.setItem(storageKey, token);
    return token ?? window.sessionStorage.getItem(storageKey) ?? "";
  } catch {
    // The launch URL still works when the browser blocks storage.
    return token ?? "";
  }
}
