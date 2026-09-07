import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { takeSessionToken } from "./session";

const workspace = { id: "local", name: "Local match", revision: 0 };
const reply = (value: unknown, status = 200) =>
  new Response(JSON.stringify(value), { status });

describe("match workspace", () => {
  it("loads and saves a name with the current revision and session credential", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(reply(workspace))
      .mockResolvedValueOnce(
        reply({ ...workspace, name: "Saturday doubles", revision: 1 }),
      );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<App sessionToken="test-session" />);
    const input = await screen.findByRole("textbox", { name: "Match name" });
    await user.clear(input);
    await user.type(input, "Saturday doubles");
    await user.click(screen.getByRole("button", { name: "Save name" }));
    expect(await screen.findByText("Match name saved.")).toBeVisible();
    expect(fetchMock).toHaveBeenLastCalledWith("/api/workspace", {
      method: "PATCH",
      headers: {
        "X-Session-Token": "test-session",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: "Saturday doubles", expected_revision: 0 }),
    });
    expect(screen.getByText("Revision 1")).toBeVisible();
  });

  it("preserves an unsaved proposal on conflict and explicitly retries with the latest revision", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(reply(workspace))
      .mockResolvedValueOnce(
        reply(
          { detail: { message: "Workspace changed", current_revision: 1 } },
          409,
        ),
      )
      .mockResolvedValueOnce(
        reply({ ...workspace, name: "Another saved name", revision: 1 }),
      )
      .mockResolvedValueOnce(
        reply({ ...workspace, name: "My proposed name", revision: 2 }),
      );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<App sessionToken="test-session" />);
    const input = await screen.findByRole("textbox", { name: "Match name" });
    await user.clear(input);
    await user.type(input, "My proposed name");
    await user.click(screen.getByRole("button", { name: "Save name" }));
    expect(await screen.findByText("Another saved name")).toBeVisible();
    expect(input).toHaveValue("My proposed name");
    expect(screen.getByRole("status")).toHaveTextContent(
      "Your unsaved name is preserved",
    );
    expect(fetchMock).toHaveBeenCalledTimes(3);
    await user.click(screen.getByRole("button", { name: "Retry save" }));
    await screen.findByText("Match name saved.");
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/workspace",
      expect.objectContaining({
        body: JSON.stringify({
          name: "My proposed name",
          expected_revision: 1,
        }),
      }),
    );
    expect(screen.getByText("Revision 2")).toBeVisible();
  });

  it("retries with the 409 revision when the latest-name refetch fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(reply(workspace))
      .mockResolvedValueOnce(
        reply(
          { detail: { message: "Workspace changed", current_revision: 1 } },
          409,
        ),
      )
      .mockRejectedValueOnce(new Error("Network error"))
      .mockResolvedValueOnce(
        reply({ ...workspace, name: "My proposed name", revision: 2 }),
      );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<App sessionToken="test-session" />);
    const input = await screen.findByRole("textbox", { name: "Match name" });
    await user.clear(input);
    await user.type(input, "My proposed name");
    await user.click(screen.getByRole("button", { name: "Save name" }));
    expect(
      await screen.findByText(/Your unsaved name is preserved/),
    ).toBeVisible();
    expect(input).toHaveValue("My proposed name");
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "could not be loaded",
    );
    expect(fetchMock).toHaveBeenCalledTimes(3);
    await user.click(screen.getByRole("button", { name: "Retry save" }));
    await screen.findByText("Match name saved.");
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/workspace",
      expect.objectContaining({
        body: JSON.stringify({
          name: "My proposed name",
          expected_revision: 1,
        }),
      }),
    );
    expect(screen.getByText("Revision 2")).toBeVisible();
  });

  it("retains unsaved input when a write fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(reply(workspace))
        .mockResolvedValueOnce(reply({}, 500)),
    );
    const user = userEvent.setup();
    render(<App sessionToken="test-session" />);
    const input = await screen.findByRole("textbox", { name: "Match name" });
    await user.clear(input);
    await user.type(input, "Keep this change");
    await user.click(screen.getByRole("button", { name: "Save name" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Request failed (500)",
    );
    expect(input).toHaveValue("Keep this change");
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Save name" })).toBeEnabled(),
    );
  });

  it("requires the coordinator launch credential", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<App sessionToken="" />);
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Open the session link",
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("removes the launch credential from the URL", () => {
    window.history.replaceState(null, "", "/?view=match#session=test-session");
    expect(takeSessionToken()).toBe("test-session");
    expect(window.location.hash).toBe("");
    expect(window.location.search).toBe("?view=match");
    expect(takeSessionToken()).toBe("test-session");
    window.sessionStorage.clear();
  });
});
