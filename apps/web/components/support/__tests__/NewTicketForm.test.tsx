import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { SupportRequestError } from "@/lib/api/support";

import {
  CHECK_ATTEMPTS,
  CHECK_INTERVAL_MS,
  SUBMIT_TIMEOUT_MS,
  submitTimeoutMs,
} from "@/components/support/NewTicketForm";
import NewTicketForm from "@/components/support/NewTicketForm";

const mocks = vi.hoisted(() => ({
  createSupportTicket: vi.fn(),
  findSupportTicketByRequestId: vi.fn(),
  push: vi.fn(),
  toastSuccess: vi.fn(),
  notFound: vi.fn(),
}));
const state = vi.hoisted(() => ({
  search: "",
  projects: [] as { id: string; name: string; space_id: string; updated_at: string; my_role: string }[],
  contentParams: [] as unknown[],
  colleagues: [] as { user_id: string; name: string; email: string }[],
  notConfigured: false,
}));
const DRAFT_KEY = "goat:support:draft:new:u1";
vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mocks.push }),
  useSearchParams: () => new URLSearchParams(state.search),
  notFound: mocks.notFound,
}));
vi.mock("@/lib/api/support", () => ({
  createSupportTicket: mocks.createSupportTicket,
  findSupportTicketByRequestId: mocks.findSupportTicketByRequestId,
  useSupportColleagues: () => ({ colleagues: state.colleagues }),
  useSupportSummary: () => ({
    summary: undefined,
    enabled: !state.notConfigured,
    notConfigured: state.notConfigured,
  }),
  SupportRequestError: class extends Error {
    constructor(
      public status: number,
      public detail: string
    ) {
      super(detail);
    }
  },
}));
vi.mock("@/lib/api/content", () => ({
  useContent: (params: unknown) => {
    state.contentParams.push(params);
    return {
      page: params ? { items: state.projects, total: state.projects.length } : undefined,
      isLoading: false,
    };
  },
  useSpaces: () => ({ spaces: [] }),
}));
vi.mock("@/lib/api/users", () => ({ useUserProfile: () => ({ userProfile: { id: "u1" } }) }));
vi.mock("react-toastify", () => ({
  toast: { success: mocks.toastSuccess, warning: vi.fn(), error: vi.fn() },
}));

const fill = (category = "bug") => {
  fireEvent.click(screen.getByText(`support_category_${category}`));
  fireEvent.change(screen.getByLabelText(/support_field_subject/), { target: { value: "Heatmap empty" } });
  fireEvent.change(screen.getByLabelText(/support_field_description/), {
    target: { value: "It shows nothing at all." },
  });
  fireEvent.click(screen.getByText("support_impact_blocking"));
};

const hangUntilAborted = () =>
  mocks.createSupportTicket.mockImplementation(
    (_i: unknown, _f: unknown, signal: AbortSignal) =>
      new Promise((_, reject) =>
        signal.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")))
      )
  );
const submitted = () => mocks.createSupportTicket.mock.calls.at(-1)![0];
const berlin = {
  id: "p1",
  name: "Berlin",
  space_id: "s1",
  updated_at: "2026-09-30T10:00:00Z",
  my_role: "viewer",
};
const pickProject = (name = "Berlin") => {
  fireEvent.mouseDown(screen.getByLabelText(/support_field_project/));
  fireEvent.click(screen.getByRole("option", { name: new RegExp(name) }));
};
const submit = () => fireEvent.click(screen.getByRole("button", { name: "support_submit" }));

describe("NewTicketForm", () => {
  beforeEach(() => {
    localStorage.clear();
    Object.values(mocks).forEach((m) => m.mockReset());
    state.search = "";
    state.projects = [];
    state.contentParams = [];
    state.colleagues = [];
    state.notConfigured = false;
  });
  afterEach(() => vi.useRealTimers());

  it("shows a spinner while sending and keeps the filled form, unflagged, after success", async () => {
    let resolve: (value: unknown) => void = () => {};
    mocks.createSupportTicket.mockImplementation(() => new Promise((r) => (resolve = r)));
    render(<NewTicketForm />);
    fill();
    fireEvent.click(screen.getByRole("button", { name: /support_submit/ }));
    // LoadingButton: disabled with a progress indicator while the request runs
    await waitFor(() => expect(screen.getByRole("progressbar")).toBeTruthy());
    expect((screen.getByRole("button", { name: /support_submit/ }) as HTMLButtonElement).disabled).toBe(true);
    await act(async () => {
      resolve({ ref: "00041", message_id: null, failed_files: [] });
    });
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/support/00041"));
    // the moment before the ticket page opens: no empty form with every field flagged
    expect(screen.queryAllByText("support_required")).toHaveLength(0);
    expect((screen.getByLabelText(/support_field_subject/) as HTMLInputElement).value).toBe("Heatmap empty");
  });

  it("submits once and opens the created ticket", async () => {
    mocks.createSupportTicket.mockResolvedValue({ ref: "00041", message_id: null, failed_files: [] });
    render(<NewTicketForm />);
    fill();
    const submit = screen.getByRole("button", { name: "support_submit" });
    fireEvent.click(submit);
    fireEvent.click(submit); // double click
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/support/00041"));
    expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1);
    const [input] = mocks.createSupportTicket.mock.calls[0];
    expect(input).toMatchObject({ subject: "Heatmap empty", category: "bug", impact: "blocking" });
    expect(input.requestId).toMatch(/^[0-9a-f-]{36}$/);
  });

  it("does not submit an incomplete form", () => {
    render(<NewTicketForm />);
    fireEvent.click(screen.getByRole("button", { name: "support_submit" }));
    expect(mocks.createSupportTicket).not.toHaveBeenCalled();
    expect(screen.getAllByText("support_required").length).toBeGreaterThan(0);
  });

  it("shows the checking state after a timeout and finds the ticket", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mocks.createSupportTicket.mockImplementation(
      (_i: unknown, _f: unknown, signal: AbortSignal) =>
        new Promise((_, reject) =>
          signal.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")))
        )
    );
    mocks.findSupportTicketByRequestId.mockResolvedValueOnce(null).mockResolvedValueOnce({ ref: "00041" });
    render(<NewTicketForm />);
    fill();
    fireEvent.click(screen.getByRole("button", { name: "support_submit" }));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });
    expect(screen.getByText("support_checking")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "support_submit" })).toBeNull(); // no retry offered
    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/support/00041"));
  });

  it.each([
    [429, "rate_limited", "support_rate_limited"],
    [422, "invalid_request", "support_invalid"],
    [413, "", "support_files_too_large"],
    [500, "", "support_unavailable"],
    [0, "", "support_unavailable"],
  ])("maps a %i failure to %s and lets the user edit and retry", async (status, detail, message) => {
    mocks.createSupportTicket.mockRejectedValue(new SupportRequestError(status, detail));
    render(<NewTicketForm />);
    fill();
    fireEvent.click(screen.getByRole("button", { name: "support_submit" }));
    expect(await screen.findByText(message)).toBeTruthy();
    expect(mocks.push).not.toHaveBeenCalled();
    expect((screen.getByRole("button", { name: "support_submit" }) as HTMLButtonElement).disabled).toBe(
      false
    );
  });

  it("restores a draft after a reload", () => {
    const { unmount } = render(<NewTicketForm />);
    fireEvent.change(screen.getByLabelText(/support_field_subject/), { target: { value: "Half written" } });
    unmount();
    render(<NewTicketForm />);
    expect((screen.getByLabelText(/support_field_subject/) as HTMLInputElement).value).toBe("Half written");
  });
  it("keeps the draft after a failed submit and clears it on success", async () => {
    mocks.createSupportTicket.mockRejectedValueOnce(new SupportRequestError(500, ""));
    mocks.createSupportTicket.mockResolvedValueOnce({ ref: "00042", message_id: null, failed_files: [] });
    render(<NewTicketForm />);
    fill();
    submit();
    await screen.findByText("support_unavailable");
    expect(JSON.parse(localStorage.getItem(DRAFT_KEY)!)).toMatchObject({ subject: "Heatmap empty" });
    submit();
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/support/00042"));
    expect(localStorage.getItem(DRAFT_KEY)).toBeNull();
    expect(submitted().requestId).toBe(mocks.createSupportTicket.mock.calls[0][0].requestId);
  });

  it("ends in the unconfirmed state after the last lookup", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    hangUntilAborted();
    mocks.findSupportTicketByRequestId.mockResolvedValue(null);
    render(<NewTicketForm />);
    fill();
    submit();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(CHECK_ATTEMPTS * CHECK_INTERVAL_MS);
    });
    expect(mocks.findSupportTicketByRequestId).toHaveBeenCalledTimes(CHECK_ATTEMPTS);
    expect(screen.getByText("support_not_confirmed")).toBeTruthy();
    expect(screen.queryByText("support_checking")).toBeNull();
    expect(mocks.push).not.toHaveBeenCalled();
  });

  it("disables Cancel while checking", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    hangUntilAborted();
    render(<NewTicketForm />);
    fill();
    submit();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });
    expect((screen.getByRole("button", { name: "support_cancel" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("reuses the request id after a remount following an aborted submit", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    hangUntilAborted();
    const first = render(<NewTicketForm />);
    fill();
    submit();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });
    const id = submitted().requestId;
    first.unmount();
    mocks.createSupportTicket.mockReset();
    mocks.createSupportTicket.mockResolvedValue({ ref: "00041", message_id: null, failed_files: [] });
    render(<NewTicketForm />);
    submit();
    await waitFor(() => expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1));
    expect(submitted().requestId).toBe(id);
    await waitFor(() => expect(localStorage.getItem(DRAFT_KEY)).toBeNull());
  });

  it("on a late success after unmount, clears the draft and toasts but does not navigate", async () => {
    let resolve!: (v: unknown) => void;
    mocks.createSupportTicket.mockReturnValue(new Promise((r) => (resolve = r)));
    const view = render(<NewTicketForm />);
    fill();
    submit();
    view.unmount();
    await act(async () => resolve({ ref: "00043", message_id: null, failed_files: [] }));
    expect(mocks.toastSuccess).toHaveBeenCalled();
    expect(mocks.push).not.toHaveBeenCalled();
    expect(localStorage.getItem(DRAFT_KEY)).toBeNull();
  });

  it("does not send the project when the picker is hidden for account & billing", async () => {
    state.projects = [berlin];
    mocks.createSupportTicket.mockResolvedValue({ ref: "00044", message_id: null, failed_files: [] });
    render(<NewTicketForm />);
    fill();
    pickProject();
    fireEvent.click(screen.getByText("support_category_account_billing"));
    submit();
    await waitFor(() => expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1));
    expect(submitted().technical).not.toHaveProperty("Project");
  });

  it("sends the selected project for other categories", async () => {
    state.projects = [berlin];
    mocks.createSupportTicket.mockResolvedValue({ ref: "00044", message_id: null, failed_files: [] });
    render(<NewTicketForm />);
    fill();
    pickProject();
    submit();
    await waitFor(() => expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1));
    expect(submitted().technical.Project).toBe("Berlin (p1)");
  });

  it("lets the user pick a project they can only view, and clear it again", async () => {
    state.projects = [berlin]; // my_role "viewer"
    mocks.createSupportTicket.mockResolvedValue({ ref: "00044", message_id: null, failed_files: [] });
    render(<NewTicketForm />);
    fill();
    const combobox = () => screen.getByLabelText(/support_field_project/) as HTMLInputElement;
    expect(combobox().value).toBe("");
    pickProject();
    expect(combobox().value).toBe("Berlin");
    // MUI only draws the clear button on hover, which leaves it out of the role queries.
    fireEvent.click(screen.getByTitle("clear"));
    expect(combobox().value).toBe("");
    submit();
    await waitFor(() => expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1));
    expect(submitted().technical).not.toHaveProperty("Project");
  });

  it("does not load or show projects for account & billing", () => {
    render(<NewTicketForm />);
    expect(state.contentParams.at(-1)).toMatchObject({ view: "recent", types: "project" });
    fireEvent.click(screen.getByText("support_category_account_billing"));
    expect(screen.queryByLabelText(/support_field_project/)).toBeNull();
    expect(state.contentParams.at(-1)).toBeNull();
  });

  it("reports only the same-origin path of ?from, without query or hash", async () => {
    mocks.createSupportTicket.mockResolvedValue({ ref: "00045", message_id: null, failed_files: [] });
    state.search = `from=${encodeURIComponent("/map/abc?token=secret#frag")}`;
    render(<NewTicketForm />);
    fill();
    submit();
    await waitFor(() => expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1));
    expect(submitted().technical.Page).toBe("/map/abc");
  });

  it("ignores a foreign-origin ?from and never falls back to the referrer", async () => {
    mocks.createSupportTicket.mockResolvedValue({ ref: "00045", message_id: null, failed_files: [] });
    state.search = `from=${encodeURIComponent("https://evil.example/phish")}`;
    render(<NewTicketForm />);
    fill();
    submit();
    await waitFor(() => expect(mocks.createSupportTicket).toHaveBeenCalledTimes(1));
    expect(submitted().technical.Page).toBe("");
  });

  it("drops unknown category/impact values and non-string fields from a stored draft", () => {
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({ category: "nope", impact: 5, subject: 12, description: "kept" })
    );
    render(<NewTicketForm />);
    expect((screen.getByLabelText(/support_field_description/) as HTMLTextAreaElement).value).toBe("kept");
    expect((screen.getByLabelText(/support_field_subject/) as HTMLInputElement).value).toBe("");
    expect(screen.queryByText("support_impact_blocking")).toBeNull(); // no category -> no impact group
    expect(screen.getAllByRole("radio").every((r) => r.getAttribute("aria-checked") === "false")).toBe(true);
  });

  it("is a radiogroup with a roving tab stop and arrow-key selection", () => {
    render(<NewTicketForm />);
    const group = () => within(screen.getAllByRole("radiogroup")[0]);
    expect(screen.getAllByRole("radiogroup")[0].getAttribute("aria-labelledby")).toBeTruthy();
    const tabStops = () =>
      group()
        .getAllByRole("radio")
        .map((r) => r.tabIndex);
    const n = group().getAllByRole("radio").length;
    expect(tabStops()).toEqual([0, ...Array(n - 1).fill(-1)]);
    fireEvent.keyDown(group().getAllByRole("radio")[0], { key: "ArrowRight" });
    expect(group().getAllByRole("radio")[1].getAttribute("aria-checked")).toBe("true");
    expect(tabStops()).toEqual(Array.from({ length: n }, (_, i) => (i === 1 ? 0 : -1)));
    fireEvent.keyDown(group().getAllByRole("radio")[1], { key: "ArrowLeft" });
    expect(group().getAllByRole("radio")[0].getAttribute("aria-checked")).toBe("true");
  });

  it("links the required error to the category group", () => {
    render(<NewTicketForm />);
    submit();
    const group = screen.getAllByRole("radiogroup")[0];
    const errorId = group.getAttribute("aria-describedby")!;
    expect(document.getElementById(errorId)?.textContent).toBe("support_required");
  });

  it("behaves like a missing page when support is off on this installation", () => {
    state.notConfigured = true;
    render(<NewTicketForm />);
    expect(mocks.notFound).toHaveBeenCalled();
  });

  it("limits the description to the length core accepts", () => {
    render(<NewTicketForm />);
    expect((screen.getByLabelText(/support_field_description/) as HTMLTextAreaElement).maxLength).toBe(20000);
  });

  it("stops offering colleagues once 20 are chosen", () => {
    state.colleagues = Array.from({ length: 21 }, (_, i) => ({
      user_id: `u${i}`,
      name: `Person ${i}`,
      email: `p${i}@x.de`,
    }));
    render(<NewTicketForm />);
    const input = screen.getByLabelText(/support_field_colleagues/);
    for (let i = 0; i < 20; i++) {
      fireEvent.mouseDown(input);
      fireEvent.click(screen.getByRole("option", { name: `Person ${i} (p${i}@x.de)` }));
    }
    fireEvent.mouseDown(input);
    expect(screen.getByRole("option", { name: "Person 20 (p20@x.de)" }).getAttribute("aria-disabled")).toBe(
      "true"
    );
    // A chosen one stays enabled, so it can still be unselected from the list.
    expect(screen.getByRole("option", { name: "Person 0 (p0@x.de)" }).getAttribute("aria-disabled")).toBe(
      "false"
    );
  });
});

describe("submitTimeoutMs", () => {
  const file = (size: number) => ({ size }) as File;

  it("is the base timeout without files", () => {
    expect(submitTimeoutMs([])).toBe(SUBMIT_TIMEOUT_MS);
  });

  it("adds the upload time at 100 kB/s", () => {
    expect(submitTimeoutMs([file(1_000_000)])).toBe(SUBMIT_TIMEOUT_MS + 10_000);
    expect(submitTimeoutMs([file(500_000), file(500_000)])).toBe(SUBMIT_TIMEOUT_MS + 10_000);
  });

  it("gives the 50 MB limit roughly 9 minutes", () => {
    const minutes = submitTimeoutMs([file(50 * 1024 * 1024)]) / 60_000;
    expect(minutes).toBeGreaterThan(8.6);
    expect(minutes).toBeLessThan(9.2);
  });
});
