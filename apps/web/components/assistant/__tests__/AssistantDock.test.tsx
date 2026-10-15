import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getDockState, registerSurface, resetAssistantStore, setDockState } from "@/lib/assistant/store";
import { setMapMode } from "@/lib/store/map/slice";

import AssistantDock from "@/components/assistant/AssistantDock";

const { pushMock, toastMock, updateMock, dispatchMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
  toastMock: { warning: vi.fn(), error: vi.fn() },
  updateMock: vi.fn(async () => ({})),
  dispatchMock: vi.fn(),
}));

vi.mock("@/hooks/store/ContextHooks", () => ({ useAppDispatch: () => dispatchMock }));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: pushMock }), usePathname: () => "/home" }));
vi.mock("react-toastify", () => ({ toast: toastMock }));
vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en" } }),
}));
vi.mock("@/lib/assistant/conversations", () => ({
  useConversations: () => ({ conversations: [], isLoading: false }),
  updateConversation: updateMock,
  refreshConversationLists: vi.fn(),
}));
vi.mock("@/components/assistant/ConversationHistory", () => ({
  default: () => <div data-testid="history" />,
}));
vi.mock("@/components/assistant/NewConversation", () => ({ default: () => <div data-testid="new" /> }));
vi.mock("@/components/assistant/ConversationPane", async () => {
  const { useDockActions } = await import("@/components/assistant/DockActions");
  return {
    default: function Pane({ onLoaded }: { onLoaded?: (detail: unknown) => void }) {
      const actions = useDockActions();
      return (
        <>
          <button
            onClick={() => void actions.openInProject("p2", { bindConversationId: "c1", partId: "m1:1" })}>
            review
          </button>
          <button
            onClick={() =>
              onLoaded?.({
                conversation: { id: "c1", project_id: null, origin_surface: "catalog", title: null },
                messages: [
                  {
                    id: "u1",
                    role: "user",
                    parts: [
                      { type: "data-context", data: { surface: "catalog" } },
                      { type: "text", text: "Wie viele " },
                      { type: "text", text: "Radwege?" },
                    ],
                  },
                  { id: "a1", role: "assistant", parts: [{ type: "text", text: "Drei." }] },
                ],
                activeRunId: null,
                access: "ok",
                projectName: null,
              })
            }>
            loaded
          </button>
        </>
      );
    },
  };
});
vi.mock("@/components/addLayer/AddLayerDialog", () => ({
  default: (props: { source: string; projectId?: string; initialFile?: File }) => (
    <div data-testid="add-layer" data-source={props.source} data-project={props.projectId ?? ""}>
      {props.initialFile?.name}
    </div>
  ),
}));

const drop = (files: File[]) =>
  fireEvent.drop(document.querySelector("[data-assistant-dock]") as Element, {
    dataTransfer: { types: ["Files"], files },
  });

beforeEach(() => {
  window.sessionStorage.clear();
  resetAssistantStore();
  vi.clearAllMocks();
  setDockState({ enabled: true, open: true });
});

describe("AssistantDock", () => {
  it("opens the upload dialog for one dropped data file, into the page's upload target", () => {
    registerSurface({
      surface: "project.map",
      project: { id: "p1", name: "Eins" },
      uploadTo: { projectId: "p1", folderId: "f1" },
      getContext: () => ({ surface: "project.map", project_id: "p1" }),
    });
    render(<AssistantDock variant="docked" />);
    drop([new File(["{}"], "netz.geojson")]);
    const dialog = screen.getByTestId("add-layer");
    expect(dialog.getAttribute("data-source")).toBe("upload");
    expect(dialog.getAttribute("data-project")).toBe("p1");
    expect(dialog.textContent).toBe("netz.geojson");
  });

  it("refuses several files and files that are not data", () => {
    render(<AssistantDock variant="docked" />);
    drop([new File(["a"], "a.csv"), new File(["b"], "b.csv")]);
    expect(toastMock.warning).toHaveBeenCalledWith("drop_one_file_only");
    drop([new File(["x"], "plan.pdf")]);
    expect(toastMock.error).toHaveBeenCalledWith("assistant_drop_not_data");
    expect(screen.queryByTestId("add-layer")).toBeNull();
  });

  it("has a resize handle on the docked panel only, not in full screen", () => {
    const { unmount } = render(<AssistantDock variant="docked" />);
    const handle = screen.getByRole("separator", { name: "assistant_resize" });
    expect(handle.closest("[data-assistant-dock]")).not.toBeNull();
    unmount();

    render(<AssistantDock variant="fullscreen" />);
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(screen.queryByRole("separator")).toBeNull();
  });

  it("starts a new conversation, expands and closes", () => {
    setDockState({ conversationId: "c1" });
    render(<AssistantDock variant="docked" />);
    fireEvent.click(screen.getByRole("button", { name: "assistant_new_conversation" }));
    expect(getDockState().conversationId).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "assistant_expand" }));
    expect(getDockState().expanded).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "close" }));
    expect(getDockState()).toMatchObject({ open: false, expanded: false });
  });

  it("binds an unbound conversation before it opens the project to review a proposal", async () => {
    setDockState({ conversationId: "c1" });
    render(<AssistantDock variant="docked" />);
    fireEvent.click(screen.getByRole("button", { name: "review" }));
    await waitFor(() => expect(pushMock).toHaveBeenCalledWith("/map/p2"));
    expect(updateMock).toHaveBeenCalledWith("c1", { project_id: "p2" });
    // The open pane learns of the binding from the store (AssistantDock.bind.test.tsx).
    expect(getDockState().bound).toEqual({ conversationId: "c1", projectId: "p2", projectName: null });
    expect(getDockState().review).toEqual({ conversationId: "c1", partId: "m1:1" });
    // The map view applies in Map mode only.
    expect(dispatchMock).toHaveBeenCalledWith(setMapMode("data"));
  });

  it("titles an untitled conversation by its first message, also when the history does not list it", () => {
    // The history lists the newest 100 only; the loaded conversation knows its own first message.
    setDockState({ conversationId: "c1" });
    render(<AssistantDock variant="docked" />);
    expect(screen.getByRole("button", { name: "assistant_untitled" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "loaded" }));
    expect(screen.getByRole("button", { name: "Wie viele Radwege?" })).toBeTruthy();
  });

  it("names the history button by the visible conversation title", () => {
    setDockState({ conversationId: "c1" });
    render(<AssistantDock variant="docked" />);
    const button = screen.getByRole("button", { name: "assistant_untitled" });
    expect(button).toHaveAccessibleDescription("assistant_history");
  });
});
