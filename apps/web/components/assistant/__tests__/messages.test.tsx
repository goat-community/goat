import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { DynamicToolUIPart } from "ai";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { registerSurface, resetAssistantStore } from "@/lib/assistant/store";
import type { AssistantMessage } from "@/lib/assistant/types";

import { DockActionsContext } from "@/components/assistant/DockActions";
import { dockActions } from "@/components/assistant/__tests__/helpers";
import AnswerDetails from "@/components/assistant/messages/AnswerDetails";
import CaveatNote from "@/components/assistant/messages/CaveatNote";
import MessageList from "@/components/assistant/messages/MessageList";
import RunStatusNote from "@/components/assistant/messages/RunStatusNote";
import SafeMarkdown, { safeHref } from "@/components/assistant/messages/SafeMarkdown";
import StepList from "@/components/assistant/messages/StepList";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en" } }),
}));

// What a card loads when shown (thumbnail, owner, date) and its preview fetch nothing here.
vi.mock("@/hooks/assistant/useItemDetails", () => ({ useItemDetails: () => ({}) }));
vi.mock("@/components/assistant/messages/ItemPreview", () => ({
  default: ({ item }: { item: { title: string } }) => <div data-testid="item-preview">{item.title}</div>,
}));
/** The open project's layers: dataset "d-in" is shown as layer 77. */
vi.mock("@/lib/api/projects", async (importOriginal) => ({
  ...(await importOriginal<Record<string, unknown>>()),
  useProjectLayers: (projectId?: string) => ({
    layers: projectId ? [{ id: 77, layer_id: "d-in" }] : undefined,
  }),
}));

const actions = dockActions();

/** The newest answer, still running, with these parts. */
const renderRunning = (parts: AssistantMessage["parts"]) =>
  render(
    <DockActionsContext.Provider value={actions}>
      <MessageList
        messages={[{ id: "r", role: "assistant", parts }]}
        busy
        conversationId="c1"
        conversationProjectId={null}
        projectName={null}
        readOnly={false}
      />
    </DockActionsContext.Provider>
  );

beforeEach(() => {
  window.sessionStorage.clear();
  resetAssistantStore();
});

const search: DynamicToolUIPart = {
  type: "dynamic-tool",
  toolName: "catalog_search",
  toolCallId: "c1",
  state: "output-available",
  input: { q: "rad" },
  output: {
    numberMatched: 1,
    results: [{ id: "ds-1", title: "Radverkehrsnetz", type: "feature", publisher: "Berlin" }],
  },
};

/** The datasets the answer recommends: only these become cards. */
const shown: DynamicToolUIPart = {
  type: "dynamic-tool",
  toolName: "catalog_show_records",
  toolCallId: "s1",
  state: "output-available",
  input: { groups: [{ records: [{ id: "ds-1" }] }] },
  output: {
    groups: [
      {
        title: "Radverkehr",
        records: [
          {
            id: "ds-1",
            title: "Radverkehrsnetz",
            type: "feature",
            publisher: "Berlin",
            note: "Das Radnetz der Stadt",
          },
        ],
      },
    ],
    not_found: [],
  },
};

describe("assistant messages", () => {
  it("renders Markdown without images, raw HTML or unsafe links", () => {
    const { container } = render(
      <SafeMarkdown>
        {
          "Text ![tracker](https://evil.example/p.png) [docs](https://goat.example) [bad](javascript:alert(1)) <b>raw</b>"
        }
      </SafeMarkdown>
    );
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("b")).toBeNull();
    const docs = screen.getByRole("link", { name: "docs" });
    expect(docs.getAttribute("href")).toBe("https://goat.example");
    expect(docs.getAttribute("target")).toBe("_blank");
    expect(docs.getAttribute("rel")).toContain("noopener");
    expect(screen.queryByRole("link", { name: "bad" })).toBeNull();
    expect(screen.getByText(/bad/)).toBeTruthy();
    expect(safeHref("/catalog/x")).toBe("/catalog/x");
    expect(safeHref("//evil.example")).toBeUndefined();
    expect(safeHref("/\\evil.example")).toBeUndefined();
    expect(safeHref("data:text/html,x")).toBeUndefined();
  });

  it("renders tables, strikethrough and bare links as GitHub does", () => {
    const { container } = render(
      <SafeMarkdown>
        {[
          "| Betriebstyp | Anzahl |",
          "|---|---:|",
          "| Fachgeschäft | 860 |",
          "| Leerstand | 218 |",
          "",
          "~~old~~ see https://goat.example/docs",
        ].join("\n")}
      </SafeMarkdown>
    );
    const table = container.querySelector("table");
    expect(table).not.toBeNull();
    expect([...container.querySelectorAll("th")].map((th) => th.textContent)).toEqual([
      "Betriebstyp",
      "Anzahl",
    ]);
    expect(container.querySelectorAll("tbody tr")).toHaveLength(2);
    expect(container.querySelector("tbody td:last-child")?.getAttribute("style")).toContain("right");
    // A wide table scrolls inside the answer.
    expect(getComputedStyle(table!.parentElement!).overflowX).toBe("auto");
    expect(container.querySelector("del")?.textContent).toBe("old");
    expect(screen.getByRole("link", { name: "https://goat.example/docs" }).getAttribute("target")).toBe(
      "_blank"
    );
    expect(container.textContent).not.toContain("|");
  });

  it("drops javascript: and data: links, HTML and images in every spelling", () => {
    const { container } = render(
      <SafeMarkdown>
        {[
          "[js](javascript:alert(1)) [JS](JaVaScRiPt:alert(1)) [ws](  javascript:alert(1))",
          "<javascript:alert(1)> [ent](&#106;avascript:alert(1)) [hex](&#x6A;avascript:alert(1)) [ref][r]",
          "[r]: javascript:alert(1)",
          "[data](data:text/html;base64,PHNjcmlwdD4=) [vb](vbscript:x) [file](file:///etc/passwd)",
          '<a href="javascript:alert(1)">html link</a> <script>alert(1)</script> <img src=x onerror=alert(1)>',
          "![i](data:image/png;base64,AAAA) [ok](https://goat.example/x) [rel](/catalog?q=a)",
        ].join("\n\n")}
      </SafeMarkdown>
    );
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    const hrefs = [...container.querySelectorAll("a")].map((a) => a.getAttribute("href"));
    expect(hrefs).toEqual(["https://goat.example/x", "/catalog?q=a"]);
    expect(container.querySelector('a[href^="javascript" i]')).toBeNull();
    // No attribute anywhere carries a script-capable URL or an event handler.
    for (const element of container.querySelectorAll("*")) {
      for (const attr of element.attributes) {
        expect(attr.name).not.toMatch(/^on/i);
        expect(attr.value).not.toMatch(/^\s*(javascript|data|vbscript|file):/i);
      }
    }
    // The dropped links keep their text.
    expect(screen.getByText(/js/)).toBeTruthy();
  });

  it("lists the steps with what each found, and shows a step's input and result on click", () => {
    render(<StepList steps={[search]} />);
    const row = screen.getByRole("button", { name: /assistant_tool_catalog_search/ });
    expect(row.textContent).toContain("assistant_result_datasets");
    fireEvent.click(row);
    expect(screen.getByText(/"q": "rad"/)).toBeTruthy();
    expect(screen.getByText(/"numberMatched": 1/)).toBeTruthy();
  });

  it("marks a running step with GOAT's mark and no result yet", () => {
    render(
      <StepList steps={[{ ...search, state: "input-available", output: undefined } as DynamicToolUIPart]} />
    );
    const row = screen.getByRole("button", { name: /assistant_tool_catalog_search/ });
    expect(row.querySelector("svg")).toBeTruthy();
    expect(row.textContent).not.toContain("assistant_result_datasets");
    expect(screen.queryByRole("progressbar")).toBeNull();
  });

  it("explains how a run ended in the UI language", () => {
    render(<RunStatusNote data={{ status: "failed", error: "GOAT AI is busy.", code: "goat_ai_busy" }} />);
    expect(screen.getByText("assistant_run_error_goat_ai_busy")).toBeTruthy();
    expect(screen.queryByText("GOAT AI is busy.")).toBeNull();
  });

  it("shows a caveat in the UI language and nothing for a kind it does not know", () => {
    const { container, rerender } = render(
      <CaveatNote data={{ kind: "fallback", text: "Your provider is down." }} />
    );
    expect(screen.getByText("assistant_caveat_fallback")).toBeTruthy();
    expect(screen.queryByText("Your provider is down.")).toBeNull();
    rerender(<CaveatNote data={{ kind: "something_new", text: "English only." }} />);
    expect(container.textContent).toBe("");
  });

  it("shows no cards for search results the answer did not recommend", () => {
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "a0", role: "assistant", parts: [search, { type: "text", text: "Nichts." }] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.queryByText("Radverkehrsnetz")).toBeNull();
  });

  it("shows the groups' headings and each dataset's note", () => {
    const two = {
      ...shown,
      output: {
        groups: [
          { title: "Grundlage", records: [{ id: "b", title: "Stadtbezirke", note: "Zum Ausschneiden" }] },
          {
            title: "Radverkehr",
            records: [
              { id: "r", title: "Radwege" },
              // Shown once, in its first group.
              { id: "b", title: "Stadtbezirke" },
            ],
          },
        ],
        not_found: [],
      },
    } as DynamicToolUIPart;
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "g", role: "assistant", parts: [two, { type: "text", text: "Lücken: keine." }] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    // Each heading carries its group's count.
    expect(screen.getByRole("heading", { name: "Grundlage · 1" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Radverkehr · 1" })).toBeTruthy();
    expect(screen.getByText("Zum Ausschneiden")).toBeTruthy();
    expect(screen.getAllByText("Stadtbezirke")).toHaveLength(1);
    // Outside a project a catalog card has its preview, and Add asks for the project.
    expect(screen.getAllByRole("button", { name: "assistant_item_preview" })).toHaveLength(2);
    expect(screen.queryByRole("button", { name: "assistant_result_add" })).toBeNull();
    expect(screen.getAllByRole("button", { name: "assistant_item_add_to_project_choose" })).toHaveLength(2);
  });

  it("still shows a flat list stored before the groups, without a heading", () => {
    const flat = {
      ...shown,
      output: { shown: [{ id: "x", title: "Altbestand" }], not_found: [] },
    } as DynamicToolUIPart;
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "f", role: "assistant", parts: [flat] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.getByText("Altbestand")).toBeTruthy();
    expect(screen.queryByRole("heading")).toBeNull();
  });

  it("shows only the answer's last list of recommended datasets", () => {
    const again = {
      ...shown,
      toolCallId: "s2",
      output: {
        groups: [
          { records: [{ id: "ds-2", title: "Fahrradstraßen", type: "feature", publisher: "Berlin" }] },
        ],
        not_found: [],
      },
    } as DynamicToolUIPart;
    const messages: AssistantMessage[] = [
      { id: "a1", role: "assistant", parts: [shown, { type: "text", text: "Mehr." }, again] },
    ];
    const spy = vi.spyOn(console, "error").mockImplementation(() => undefined);
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={messages}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    // The earlier list is replaced by the later one, across a text in between...
    expect(screen.queryByText("Radverkehrsnetz")).toBeNull();
    expect(screen.getAllByText("Fahrradstraßen")).toHaveLength(1);
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
    // ...and within one group of steps.
    cleanup();
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "a2", role: "assistant", parts: [shown, again] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.queryByText("Radverkehrsnetz")).toBeNull();
    expect(screen.getAllByText("Fahrradstraßen")).toHaveLength(1);
  });

  it("gives each card one button by kind and page, and opens one preview at a time", async () => {
    const own = {
      type: "dynamic-tool",
      toolName: "core_show_items",
      toolCallId: "o1",
      state: "output-available",
      input: {},
      output: {
        groups: [
          {
            title: "Radverkehr",
            items: [
              { kind: "project", id: "p2", name: "Radnetz Nord", note: "Viele Radwege" },
              { kind: "layer", id: "11", project_id: "p1", project_name: "Eins", name: "Radwege" },
              {
                kind: "layer",
                id: "40",
                project_id: "p2",
                dataset_id: "d4",
                project_name: "Radnetz Nord",
                name: "Abstellanlagen",
              },
              { kind: "dataset", id: "d1", dataset_id: "d1", name: "Fahrradständer" },
              // Already in the open project, as layer 77.
              { kind: "dataset", id: "d-in", dataset_id: "d-in", name: "Zählstellen" },
              { kind: "workflow", id: "w1", project_id: "p1", project_name: "Eins", name: "Einzugsgebiete" },
            ],
          },
        ],
        not_found: [],
        left_out: [],
      },
    } as DynamicToolUIPart;
    registerSurface({
      surface: "project.map",
      project: { id: "p1", name: "Eins" },
      uploadTo: { projectId: "p1" },
      getContext: () => ({ surface: "project.map", project_id: "p1" }),
    });
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "o", role: "assistant", parts: [own, { type: "text", text: "Treffer." }] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.getByText("Viele Radwege")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "assistant_item_open_project" }));
    expect(actions.openProject).toHaveBeenCalledWith("p2");
    // A workflow opens in its project's workflow editor.
    fireEvent.click(screen.getByRole("button", { name: "assistant_item_open_workflow" }));
    expect(actions.openInProjectMode).toHaveBeenCalledWith("p1", "workflows", "w1");
    // In the open project: Zoom only, for its own layer and for a dataset it already shows.
    const zooms = screen.getAllByRole("button", { name: "assistant_item_zoom_to_layer" });
    expect(zooms.filter((button) => button.textContent === "assistant_item_zoom")).toHaveLength(2);
    fireEvent.click(zooms.filter((button) => button.textContent === "assistant_item_zoom")[1]);
    expect(actions.zoomToLayer).toHaveBeenCalledWith(77);
    // The other layer and the dataset have a preview (a project has none), one open at a time.
    const previews = screen.getAllByRole("button", { name: "assistant_item_preview" });
    expect(previews).toHaveLength(2);
    fireEvent.click(previews[0]);
    expect(screen.getByTestId("item-preview").textContent).toBe("Abstellanlagen");
    fireEvent.click(screen.getAllByRole("button", { name: "assistant_item_preview" })[0]);
    expect(screen.getAllByTestId("item-preview").map((node) => node.textContent)).toEqual(["Fahrradständer"]);
    const adds = screen.getAllByRole("button", { name: "assistant_result_add" });
    expect(adds).toHaveLength(2);
    fireEvent.click(adds[1]);
    // Added: the card shows it and offers Zoom to the new layer instead of Add.
    expect(await screen.findByText("assistant_item_added")).toBeTruthy();
    expect(actions.addToProject).toHaveBeenCalledWith(expect.objectContaining({ id: "d1" }), undefined);
    expect(screen.getAllByRole("button", { name: "assistant_result_add" })).toHaveLength(1);
  });

  it("does not show the server's text of a failed step", () => {
    const failed = {
      ...search,
      state: "output-error",
      output: undefined,
      errorText: "Internal English detail",
    };
    render(<StepList steps={[failed as unknown as DynamicToolUIPart]} />);
    fireEvent.click(screen.getByRole("button", { name: /assistant_tool_catalog_search/ }));
    expect(screen.getByText(/assistant_step_failed/)).toBeTruthy();
    expect(screen.queryByText(/Internal English detail/)).toBeNull();
  });

  it("shows model, provider and tokens in the answer details", () => {
    const { rerender } = render(
      <AnswerDetails
        usage={{
          model: "claude-x",
          provider: "bedrock",
          input_tokens: 15,
          output_tokens: 5,
          cache_read_tokens: 2,
        }}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: "assistant_details" }));
    expect(screen.getByText("claude-x")).toBeTruthy();
    expect(screen.getByText("bedrock")).toBeTruthy();
    expect(screen.getByText("15")).toBeTruthy();
    // The popover stays open across the rerender: an answer without recorded usage says so.
    rerender(<AnswerDetails usage={undefined} />);
    expect(screen.getByText("assistant_details_none")).toBeTruthy();
  });

  it("renders a conversation: context chips, text, steps, results, caveats and the run status", () => {
    const messages: AssistantMessage[] = [
      {
        id: "u1",
        role: "user",
        parts: [
          { type: "text", text: "Radwege?" },
          { type: "data-context", data: { surface: "catalog", q: "rad" } },
        ],
      },
      {
        id: "a1",
        role: "assistant",
        parts: [
          { type: "step-start" },
          search,
          shown,
          { type: "text", text: "Ein Datensatz passt." },
          { type: "data-caveat", data: { kind: "fallback", text: "English text" } },
          { type: "data-run-status", data: { status: "cancelled", error: null, code: null } },
        ],
      },
    ];
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={messages}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.getByText("Radwege?")).toBeTruthy();
    expect(screen.getByText("assistant_chip_search")).toBeTruthy();
    expect(screen.getByText("Ein Datensatz passt.")).toBeTruthy();
    expect(screen.getByText("Radverkehrsnetz")).toBeTruthy();
    expect(screen.getByText("assistant_caveat_fallback")).toBeTruthy();
    // The server's own (English) caveat text is never shown.
    expect(screen.queryByText("English text")).toBeNull();
    expect(screen.getByText("assistant_run_cancelled")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "assistant_item_preview" }));
    expect(screen.getByTestId("item-preview").textContent).toBe("Radverkehrsnetz");
  });
});

describe("the Answering line", () => {
  it("shows before the first step and between steps", () => {
    renderRunning([]);
    expect(screen.getByText("assistant_running")).toBeTruthy();
    cleanup();
    // Every step done, the model choosing its next one or writing its answer.
    renderRunning([search]);
    expect(screen.getByText("assistant_running")).toBeTruthy();
  });

  it("stays while a step runs and while text streams in, so it never flickers", () => {
    const runningStep: DynamicToolUIPart = {
      type: "dynamic-tool",
      toolName: "catalog_search",
      toolCallId: "c2",
      state: "input-available",
      input: { q: "bus" },
    };
    renderRunning([search, runningStep]);
    expect(screen.getByText("assistant_running")).toBeTruthy();
    cleanup();
    renderRunning([search, { type: "text", text: "Ich habe", state: "streaming" }]);
    expect(screen.getByText("assistant_running")).toBeTruthy();
  });

  it("shows right after sending, before the answer has started", () => {
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "u", role: "user", parts: [{ type: "text", text: "Hallo" }] }]}
          busy
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.getByText("assistant_running")).toBeTruthy();
  });

  it("is gone once the answer is done", () => {
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "d", role: "assistant", parts: [search] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
    expect(screen.queryByText("assistant_running")).toBeNull();
  });
});

describe("card tooltips", () => {
  /** jsdom lays nothing out: these sizes stand in for a clamped (cut) or a fitting text. */
  const sizes = (scroll: number, client: number) => {
    Object.defineProperty(HTMLElement.prototype, "scrollHeight", { configurable: true, get: () => scroll });
    Object.defineProperty(HTMLElement.prototype, "clientHeight", { configurable: true, get: () => client });
  };
  afterEach(() => {
    delete (HTMLElement.prototype as { scrollHeight?: number }).scrollHeight;
    delete (HTMLElement.prototype as { clientHeight?: number }).clientHeight;
  });

  const renderCard = () =>
    render(
      <DockActionsContext.Provider value={actions}>
        <MessageList
          messages={[{ id: "t", role: "assistant", parts: [search, shown, { type: "text", text: "Hier." }] }]}
          busy={false}
          conversationId="c1"
          conversationProjectId={null}
          projectName={null}
          readOnly={false}
        />
      </DockActionsContext.Provider>
    );
  const hover = (element: HTMLElement) => {
    fireEvent.mouseEnter(element);
    fireEvent.mouseOver(element);
  };
  const settle = () => new Promise((resolve) => setTimeout(resolve, 250));

  it("repeats a title or note on hover only when it is cut", async () => {
    sizes(40, 40);
    renderCard();
    hover(screen.getByText("Radverkehrsnetz"));
    hover(screen.getByText("Das Radnetz der Stadt"));
    await settle();
    expect(screen.queryByRole("tooltip")).toBeNull();
    cleanup();

    sizes(80, 40);
    renderCard();
    hover(screen.getByText("Radverkehrsnetz"));
    expect((await screen.findByRole("tooltip")).textContent).toBe("Radverkehrsnetz");
  });

  it("keeps a meta tooltip that adds a label to the words on the card", async () => {
    sizes(20, 20);
    renderCard();
    hover(screen.getByText("Berlin"));
    expect((await screen.findByRole("tooltip")).textContent).toBe("assistant_item_publisher: Berlin");
  });
});
