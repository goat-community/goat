/**
 * Task 6: the layouts panel opens the shared template browser (locked to
 * "layout", every source shown) instead of the old hardcoded picker, and its kebab
 * gains "Save as template". The heavy template components (`TemplateBrowser`,
 * `UseTemplateFlow`, `SaveTemplateDialog`) are stubbed so this suite can
 * assert on the props the panel wires them with and drive their callbacks.
 */
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { Project } from "@/lib/validations/project";
import type { ReportLayout } from "@/lib/validations/reportLayout";
import type { TemplateRead, TemplateUseResult } from "@/lib/validations/template";

import ReportsConfigPanel from "@/components/reports/panels/ReportsConfigPanel";

const {
  useReportLayoutsMock,
  createReportLayoutMock,
  mutateMock,
  templateBrowserPropsSpy,
  templateFlowPropsSpy,
  saveTemplateDialogPropsSpy,
  toastSuccessMock,
  updateReportLayoutMock,
} = vi.hoisted(() => ({
  useReportLayoutsMock: vi.fn(),
  createReportLayoutMock: vi.fn(),
  mutateMock: vi.fn(),
  templateBrowserPropsSpy: vi.fn(),
  templateFlowPropsSpy: vi.fn(),
  saveTemplateDialogPropsSpy: vi.fn(),
  toastSuccessMock: vi.fn(),
  updateReportLayoutMock: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => (opts ? `${key}:${JSON.stringify(opts)}` : key),
  }),
  Trans: ({ i18nKey }: { i18nKey: string }) => <span>{i18nKey}</span>,
}));

vi.mock("react-toastify", () => ({ toast: { success: toastSuccessMock, error: vi.fn(), info: vi.fn() } }));

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));

vi.mock("@/lib/api/reportLayouts", () => ({
  useReportLayouts: (...args: unknown[]) => useReportLayoutsMock(...args),
  createReportLayout: (...args: unknown[]) => createReportLayoutMock(...args),
  deleteReportLayout: vi.fn(),
  duplicateReportLayout: vi.fn(),
  updateReportLayout: (...args: unknown[]) => updateReportLayoutMock(...args),
}));

vi.mock("@/lib/api/layers", () => ({
  useLayerQueryables: () => ({ queryables: undefined }),
}));

vi.mock("@/hooks/reports/useAtlasFeatures", () => ({
  useAtlasFeatures: () => ({ totalPages: 0, wasTruncated: false, totalFeatureCount: 0 }),
}));

vi.mock("@/hooks/reports/usePrintConfig", () => ({
  usePrintConfig: () => ({ atlasMaxPages: 100, isLoading: false }),
}));

vi.mock("@/hooks/useExportReport", () => ({
  useExportReport: () => ({ isBusy: false, exportReport: vi.fn() }),
}));

vi.mock("@/components/templates/TemplateBrowser", () => ({
  default: (props: {
    open?: boolean;
    lockedKind?: string;
    initialSource?: string;
    onUse: (template: TemplateRead) => void;
  }) => {
    templateBrowserPropsSpy(props);
    if (!props.open) return null;
    return <button onClick={() => props.onUse(fakeTemplate)}>fake-use-template</button>;
  },
}));

vi.mock("@/components/templates/UseTemplateFlow", () => ({
  default: (props: { onDone: (result: TemplateUseResult) => void; onClose: () => void }) => {
    templateFlowPropsSpy(props);
    return (
      <div>
        <button onClick={() => props.onDone(fakeUseResult)}>fake-use-done</button>
        <button onClick={props.onClose}>fake-use-close</button>
      </div>
    );
  },
}));

vi.mock("@/components/templates/SaveTemplateDialog", () => ({
  default: (props: { onSaved: (template: TemplateRead) => void; onClose: () => void }) => {
    saveTemplateDialogPropsSpy(props);
    return (
      <div>
        <button onClick={() => props.onSaved(fakeSavedTemplate)}>fake-save-template</button>
      </div>
    );
  },
}));

const fakeTemplate: TemplateRead = {
  id: "template-1",
  name: "Bus network report",
  description: null,
  categories: [],
  thumbnail_url: null,
  space_id: "space-1",
  folder_id: "folder-1",
  created_by: null,
  payload_kind: "layout",
  kinds: ["layout"],
  inputs: [],
  ships_data: false,
  catalog_status: "published",
  source_ref: {},
  datasets_needing_share: [],
  my_role: "viewer",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const fakeSavedTemplate: TemplateRead = { ...fakeTemplate, id: "template-2", name: "Saved layout" };

const fakeUseResult: TemplateUseResult = {
  project_id: "project-1",
  workflow_id: null,
  layout_id: "layout-new",
  added_layer_project_ids: [],
  unresolved_inputs: [],
  copy_jobs: [],
};

const project: Project = { id: "project-1" } as Project;

const layoutA: ReportLayout = {
  id: "layout-a",
  name: "Layout A",
  is_default: true,
  thumbnail_url: null,
  config: {
    page: { size: "A4", orientation: "portrait", margins: { top: 10, right: 10, bottom: 10, left: 10 } },
    layout: { type: "grid", columns: 12, rows: 12, gap: 5 },
    elements: [],
  },
} as unknown as ReportLayout;

beforeEach(() => {
  useReportLayoutsMock.mockReset();
  mutateMock.mockReset().mockResolvedValue(undefined);
  templateBrowserPropsSpy.mockReset();
  templateFlowPropsSpy.mockReset();
  saveTemplateDialogPropsSpy.mockReset();
  toastSuccessMock.mockReset();
  updateReportLayoutMock.mockReset().mockResolvedValue(undefined);
  useReportLayoutsMock.mockReturnValue({
    reportLayouts: [layoutA],
    isLoading: false,
    isError: undefined,
    mutate: mutateMock,
    isValidating: false,
  });
});

describe("ReportsConfigPanel — template browser integration", () => {
  it("opens the template browser locked to layout, with no source filter, from the New menu", async () => {
    const user = userEvent.setup();
    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={vi.fn()} />);

    // Nothing is mounted while the browser is closed — it would otherwise
    // run its own template/space/pin requests on every panel mount.
    expect(templateBrowserPropsSpy).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "new" }));
    await user.click(await screen.findByRole("menuitem", { name: "from_template" }));

    expect(templateBrowserPropsSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({ open: true, lockedKind: "layout" })
    );
    expect(templateBrowserPropsSpy.mock.lastCall?.[0]).not.toHaveProperty("initialSource");
    expect(screen.getByText("fake-use-template")).toBeInTheDocument();
  });

  it("creates a layout from scratch from the New menu", async () => {
    const user = userEvent.setup();
    createReportLayoutMock.mockResolvedValueOnce({ id: "new-layout" });
    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "new" }));
    await user.click(await screen.findByRole("menuitem", { name: "from_scratch" }));

    expect(createReportLayoutMock).toHaveBeenCalledWith(
      "project-1",
      expect.objectContaining({ is_default: false, config: expect.objectContaining({ elements: [] }) })
    );
  });

  it("auto-opens the template browser when no layouts exist", () => {
    useReportLayoutsMock.mockReturnValue({
      reportLayouts: [],
      isLoading: false,
      isError: undefined,
      mutate: mutateMock,
      isValidating: false,
    });

    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={vi.fn()} />);

    expect(templateBrowserPropsSpy).toHaveBeenLastCalledWith(expect.objectContaining({ open: true }));
  });

  it("picking a template from the browser opens UseTemplateFlow in the current project", async () => {
    const user = userEvent.setup();
    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "new" }));
    await user.click(await screen.findByRole("menuitem", { name: "from_template" }));
    await user.click(screen.getByText("fake-use-template"));

    expect(templateFlowPropsSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        template: fakeTemplate,
        context: { kind: "in_project", projectId: "project-1" },
      })
    );
    // The browser unmounts once a template is picked.
    expect(screen.queryByText("fake-use-template")).not.toBeInTheDocument();
  });

  it("onDone from UseTemplateFlow refreshes the layout list and closes the flow", async () => {
    const onSelectReport = vi.fn();
    const user = userEvent.setup();
    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={onSelectReport} />);

    await user.click(screen.getByRole("button", { name: "new" }));
    await user.click(await screen.findByRole("menuitem", { name: "from_template" }));
    await user.click(screen.getByText("fake-use-template"));
    await user.click(screen.getByText("fake-use-done"));

    expect(mutateMock).toHaveBeenCalled();
    // The flow closes itself once it reports done.
    expect(screen.queryByText("fake-use-done")).not.toBeInTheDocument();
  });

  it("shows 4 items in the layout kebab menu, including Save as template", async () => {
    const user = userEvent.setup();
    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "more_options" }));

    const menu = await screen.findByText("save_as_template");
    expect(menu).toBeInTheDocument();
    expect(screen.getByText("rename")).toBeInTheDocument();
    expect(screen.getByText("duplicate")).toBeInTheDocument();
    expect(screen.getByText("delete")).toBeInTheDocument();
  });

  it("kebab Save as template opens SaveTemplateDialog with the layout source and toasts on save", async () => {
    const user = userEvent.setup();
    render(<ReportsConfigPanel project={project} selectedReport={null} onSelectReport={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "more_options" }));
    await user.click(screen.getByText("save_as_template"));

    expect(saveTemplateDialogPropsSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        source: { kind: "layout", project_id: "project-1", layout_id: "layout-a" },
        defaultName: "Layout A",
      })
    );

    await user.click(screen.getByText("fake-save-template"));
    expect(toastSuccessMock).toHaveBeenCalled();
  }, 15000);

  it("prefers initialLayoutId (a template result's ?layout=<id>) over reportLayouts[0] on load", () => {
    const layoutB: ReportLayout = { ...layoutA, id: "layout-b", name: "Layout B" };
    useReportLayoutsMock.mockReturnValue({
      reportLayouts: [layoutA, layoutB],
      isLoading: false,
      isError: undefined,
      mutate: mutateMock,
      isValidating: false,
    });
    const onSelectReport = vi.fn();

    render(
      <ReportsConfigPanel
        project={project}
        selectedReport={null}
        onSelectReport={onSelectReport}
        initialLayoutId="layout-b"
      />
    );

    expect(onSelectReport).toHaveBeenCalledWith(expect.objectContaining({ id: "layout-b" }));
  });

  it("falls back to reportLayouts[0] when initialLayoutId doesn't match a loaded layout", () => {
    const onSelectReport = vi.fn();

    render(
      <ReportsConfigPanel
        project={project}
        selectedReport={null}
        onSelectReport={onSelectReport}
        initialLayoutId="missing-id"
      />
    );

    expect(onSelectReport).toHaveBeenCalledWith(expect.objectContaining({ id: "layout-a" }));
  });
});

/**
 * Page settings: the sheet the layout prints on. A2, A1 and a Custom size
 * join the named sizes; the DPI list greys out what the sheet cannot render;
 * a sheet change on a layout with elements asks whether to stretch them onto
 * the new sheet.
 */
const withPage = (page: Record<string, unknown>, elements: unknown[] = []): ReportLayout =>
  ({
    ...layoutA,
    config: {
      ...layoutA.config,
      page: { ...layoutA.config.page, ...page },
      elements,
    },
  }) as unknown as ReportLayout;

const mapElement = {
  id: "el-1",
  type: "map",
  position: { x: 15, y: 32, width: 180, height: 150, z_index: 0 },
  config: {},
};

/** Opens the MUI select whose rendered value reads `displayed`. */
const openSelect = (displayed: string) => {
  const trigger = screen.getByText(displayed).closest('[role="combobox"]');
  if (!trigger) throw new Error(`no select shows ${displayed}`);
  fireEvent.mouseDown(trigger);
  return screen.findByRole("listbox");
};

const renderWith = (layout: ReportLayout) => {
  useReportLayoutsMock.mockReturnValue({
    reportLayouts: [layout],
    isLoading: false,
    isError: undefined,
    mutate: mutateMock,
    isValidating: false,
  });
  return render(<ReportsConfigPanel project={project} selectedReport={layout} onSelectReport={vi.fn()} />);
};

const savedPage = () => {
  const call = updateReportLayoutMock.mock.calls.at(-1);
  if (!call) throw new Error("nothing saved");
  return (call[2] as { config: { page: Record<string, unknown>; elements: (typeof mapElement)[] } }).config;
};

describe("ReportsConfigPanel — page sizes", () => {
  it("offers A2 and A1 among the page sizes", async () => {
    renderWith(layoutA);
    const list = await openSelect("A4");
    expect(within(list).getByRole("option", { name: "A2" })).toBeInTheDocument();
    expect(within(list).getByRole("option", { name: "A1" })).toBeInTheDocument();
  });

  it("switching to Custom shows width and height prefilled with the current sheet and saves them", async () => {
    const user = userEvent.setup();
    renderWith(layoutA);
    const list = await openSelect("A4");
    await user.click(within(list).getByRole("option", { name: "custom" }));

    await waitFor(() => expect(screen.getByRole("spinbutton", { name: "width" })).toHaveValue(210));
    await waitFor(() => expect(screen.getByRole("spinbutton", { name: "height" })).toHaveValue(297));
    await waitFor(() =>
      expect(savedPage().page).toEqual(expect.objectContaining({ size: "Custom", width: 210, height: 297 }))
    );
  });

  it("does not save a custom side outside 50–1500 mm and says why", async () => {
    const user = userEvent.setup();
    renderWith(withPage({ size: "Custom", width: 300, height: 200 }));
    const width = screen.getByRole("spinbutton", { name: "width" });
    await user.clear(width);
    await user.type(width, "20");
    await user.tab();

    expect(screen.getByText(/page_side_out_of_range/)).toBeInTheDocument();
    expect(updateReportLayoutMock).not.toHaveBeenCalled();
  });

  it("saves a valid custom width once typed and left", async () => {
    const user = userEvent.setup();
    renderWith(withPage({ size: "Custom", width: 300, height: 200 }));
    const width = screen.getByRole("spinbutton", { name: "width" });
    await user.clear(width);
    await user.type(width, "400");
    await user.tab();

    await waitFor(() =>
      expect(savedPage().page).toEqual(expect.objectContaining({ width: 400, height: 200 }))
    );
  });

  it("on a Custom page, choosing the other orientation swaps width and height", async () => {
    const user = userEvent.setup();
    renderWith(withPage({ size: "Custom", width: 300, height: 200 }));
    // 300 × 200 is the wider way round, so the control reads horizontal.
    const list = await openSelect("horizontal");
    await user.click(within(list).getByRole("option", { name: "vertical" }));

    await waitFor(() =>
      expect(savedPage().page).toEqual(expect.objectContaining({ width: 200, height: 300 }))
    );
  });

  it("greys out DPI options the sheet cannot render and shows the export size", async () => {
    renderWith(withPage({ size: "A1", orientation: "portrait", dpi: 300 }));
    expect(screen.getByText(/export_pixels.*7016.*9933/)).toBeInTheDocument();
    const list = await openSelect("300 (High)");
    await waitFor(() =>
      expect(within(list).getByRole("option", { name: /600 \(Print\)/ })).toHaveAttribute(
        "aria-disabled",
        "true"
      )
    );
    await waitFor(() =>
      expect(within(list).getByRole("option", { name: /300 \(High\)/ })).not.toHaveAttribute(
        "aria-disabled",
        "true"
      )
    );
  });

  it("asks whether to scale the elements when the sheet changes on a layout that has some", async () => {
    const user = userEvent.setup();
    renderWith(withPage({}, [mapElement]));
    const list = await openSelect("A4");
    await user.click(within(list).getByRole("option", { name: "A3" }));

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("scale_elements_title")).toBeInTheDocument();
    expect(within(dialog).getByText(/scale_elements_prompt.*"count":1/)).toBeInTheDocument();
    expect(updateReportLayoutMock).not.toHaveBeenCalled();
  });

  it("Scale elements saves the elements stretched onto the new sheet", async () => {
    const user = userEvent.setup();
    renderWith(withPage({}, [mapElement]));
    const list = await openSelect("A4");
    await user.click(within(list).getByRole("option", { name: "A3" }));
    await user.click(await screen.findByRole("button", { name: "scale_elements" }));

    await waitFor(() => expect(updateReportLayoutMock).toHaveBeenCalled());
    const saved = savedPage();
    expect(saved.page.size).toBe("A3");
    expect(saved.elements[0].position.x).toBeCloseTo(15 * (297 / 210), 3);
    expect(saved.elements[0].position.height).toBeCloseTo(150 * (420 / 297), 3);
  });

  it("Keep sizes saves the new sheet with the elements where they were", async () => {
    const user = userEvent.setup();
    renderWith(withPage({}, [mapElement]));
    const list = await openSelect("A4");
    await user.click(within(list).getByRole("option", { name: "A3" }));
    await user.click(await screen.findByRole("button", { name: "keep_sizes" }));

    await waitFor(() => expect(updateReportLayoutMock).toHaveBeenCalled());
    const saved = savedPage();
    expect(saved.page.size).toBe("A3");
    expect(saved.elements[0].position).toEqual(mapElement.position);
  });

  it("closing the prompt cancels the change and puts the old size back", async () => {
    const user = userEvent.setup();
    renderWith(withPage({}, [mapElement]));
    const list = await openSelect("A4");
    await user.click(within(list).getByRole("option", { name: "A3" }));
    await screen.findByRole("dialog");
    await user.keyboard("{Escape}");

    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(updateReportLayoutMock).not.toHaveBeenCalled();
    expect(screen.getByText("A4")).toBeInTheDocument();
  });

  it("changes the sheet without asking when the layout has no elements", async () => {
    const user = userEvent.setup();
    renderWith(layoutA);
    const list = await openSelect("A4");
    await user.click(within(list).getByRole("option", { name: "A3" }));

    await waitFor(() => expect(savedPage().page.size).toBe("A3"));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
