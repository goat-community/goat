import { fireEvent, render, screen } from "@testing-library/react";
import { withNuqsTestingAdapter } from "nuqs/adapters/testing";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { TemplateRead, TemplateUseResult } from "@/lib/validations/template";

import CatalogPage from "@/app/(dashboard)/catalog/page";

const { pushMock, useCatalogDatasetsMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
  useCatalogDatasetsMock: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en" } }),
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: pushMock }) }));

vi.mock("@/lib/api/catalog", () => ({
  useCatalogAggregations: () => ({ aggregations: [], isLoading: false }),
  useCatalogDatasets: useCatalogDatasetsMock,
}));
vi.mock("@/lib/api/favorites", () => ({
  useFavoriteStars: () => ({ starred: {}, toggleStar: vi.fn() }),
}));
vi.mock("@/hooks/catalog/useCatalogFacetSections", () => ({
  useCatalogFacetSections: () => ({
    sections: [],
    facetLabel: (v: string) => v,
    optionLabel: (v: string) => v,
  }),
}));

// The dataset sidebar/toolbar are the STAC-backed half of the page — kept
// out of scope here so the test can focus on the tab switch itself.
vi.mock("@/components/dashboard/catalog/CatalogFilterPanel", () => ({
  default: () => <div data-testid="filter-panel" />,
}));
vi.mock("@/components/dashboard/catalog/CatalogToolbar", () => ({
  default: () => <div data-testid="catalog-toolbar" />,
}));

const templateBrowserOnUse = vi.fn();
vi.mock("@/components/templates/TemplateBrowser", () => ({
  default: (props: { mode: string; initialSource?: string; onUse: (t: TemplateRead) => void }) => {
    templateBrowserOnUse.mockImplementation(props.onUse);
    return (
      <div data-testid="template-browser" data-mode={props.mode} data-source={props.initialSource ?? ""}>
        <button onClick={() => props.onUse(templateFixture)}>use-template</button>
      </div>
    );
  },
}));

const useTemplateFlowOnDone = vi.fn();
vi.mock("@/components/templates/UseTemplateFlow", () => ({
  default: (props: { onDone: (result: TemplateUseResult) => void }) => {
    useTemplateFlowOnDone.mockImplementation(props.onDone);
    return (
      <div data-testid="use-template-flow">
        <button onClick={() => props.onDone(templateUseResultFixture)}>finish</button>
      </div>
    );
  },
}));

const templateFixture: TemplateRead = {
  datasets_needing_share: [],
  id: "11111111-1111-1111-1111-111111111111",
  name: "Starter",
  description: null,
  categories: [],
  thumbnail_url: null,
  space_id: "22222222-2222-2222-2222-222222222222",
  folder_id: "33333333-3333-3333-3333-333333333333",
  created_by: null,
  payload_kind: "project",
  kinds: ["layout"],
  inputs: [],
  ships_data: false,
  catalog_status: "published",
  source_ref: {},
  my_role: "viewer",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const templateUseResultFixture: TemplateUseResult = {
  project_id: "44444444-4444-4444-4444-444444444444",
  workflow_id: null,
  layout_id: null,
  added_layer_project_ids: [],
  unresolved_inputs: [],
  copy_jobs: [],
};

const renderPage = (searchParams?: string) =>
  render(<CatalogPage />, { wrapper: withNuqsTestingAdapter({ searchParams }) });

describe("CatalogPage — Templates tab", () => {
  beforeEach(() => {
    pushMock.mockReset();
    useCatalogDatasetsMock.mockReset();
    useCatalogDatasetsMock.mockReturnValue({
      datasets: [],
      total: 0,
      isLoading: false,
      isValidating: false,
    });
  });

  it("defaults to the datasets tab, with the dataset grid intact", () => {
    renderPage();

    expect(screen.getByTestId("filter-panel")).toBeInTheDocument();
    expect(screen.getByTestId("catalog-toolbar")).toBeInTheDocument();
    expect(screen.queryByTestId("template-browser")).not.toBeInTheDocument();
  });

  it("switches to the Templates tab, hiding the dataset sidebar/grid", () => {
    renderPage();

    fireEvent.click(screen.getByRole("button", { name: "templates" }));

    // Read off the DOM property rather than a matcher: the repo's ESLint
    // setup reads jest-dom's `toHaveAttribute` as Playwright's (async)
    // matcher of the same name.
    const browser = screen.getByTestId("template-browser");
    expect(browser.getAttribute("data-mode")).toBe("inline");
    // Inline mode is the GOAT shelf by itself, so the tab passes no source
    // of its own and offers nothing that would change it.
    expect(browser.getAttribute("data-source")).toBe("");
    expect(screen.queryByTestId("filter-panel")).not.toBeInTheDocument();
    expect(screen.queryByTestId("catalog-toolbar")).not.toBeInTheDocument();
  });

  it("deep links to ?tab=templates, rendering the browser on first paint", () => {
    renderPage("?tab=templates");

    expect(screen.getByTestId("template-browser")).toBeInTheDocument();
    expect(screen.queryByTestId("filter-panel")).not.toBeInTheDocument();
  });

  it("opens Use template on a pick and navigates to the result on done", () => {
    renderPage("?tab=templates");

    fireEvent.click(screen.getByRole("button", { name: "use-template" }));
    expect(screen.getByTestId("use-template-flow")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "finish" }));
    expect(pushMock).toHaveBeenCalledWith(`/map/${templateUseResultFixture.project_id}`);
    expect(screen.queryByTestId("use-template-flow")).not.toBeInTheDocument();
  });
});
