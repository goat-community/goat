import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import HomeHero from "@/components/dashboard/home/HomeHero";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en" } }),
}));
const { newProjectButtonMock } = vi.hoisted(() => ({ newProjectButtonMock: vi.fn() }));

// The shared "New project" menu owns its own dialogs (template browser,
// project import); the hero only has to place it and hand it a folder.
vi.mock("@/components/dashboard/common/NewProjectMenu", () => ({
  NewProjectButton: (props: { location: { folderId?: string } }) => {
    newProjectButtonMock(props);
    return <button type="button">new_project</button>;
  },
}));

const noop = () => undefined;

const renderHero = (overrides: Partial<Parameters<typeof HomeHero>[0]> = {}) =>
  render(
    <HomeHero
      stage="getting_started"
      firstName="Marco"
      search={<div data-testid="search-slot" />}
      homeFolderId="home-1"
      onAddDataset={noop}
      onBrowseCatalog={noop}
      showHelp
      mobile={false}
      {...overrides}
    />
  );

describe("HomeHero", () => {
  beforeEach(() => {
    newProjectButtonMock.mockReset();
  });

  it("greets a first-time caller, without the search slot or quick actions", () => {
    renderHero({ stage: "new" });

    expect(screen.getByText("welcome_to_goat")).toBeInTheDocument();
    expect(screen.queryByTestId("search-slot")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "new_project" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "upload_dataset" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "browse_catalog" })).not.toBeInTheDocument();
  });

  it("still welcomes a caller who is getting started to GOAT, with the search slot and quick actions", () => {
    renderHero({ stage: "getting_started" });

    expect(screen.getByText("welcome_to_goat")).toBeInTheDocument();
    expect(screen.queryByText("welcome_back")).not.toBeInTheDocument();
    expect(screen.getByTestId("search-slot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "new_project" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "upload_dataset" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "browse_catalog" })).toBeInTheDocument();
  });

  it("files a project created from the hero into the caller's personal home folder", () => {
    renderHero({ stage: "getting_started", homeFolderId: "home-1" });

    expect(newProjectButtonMock).toHaveBeenCalledWith(
      expect.objectContaining({ location: { folderId: "home-1" } })
    );
  });

  it("swaps the greeting for skeletons while loading, keeping search and the quick actions", () => {
    const { container } = renderHero({ stage: "established", loading: true, showHelp: false });

    expect(screen.queryByText("welcome_back")).not.toBeInTheDocument();
    expect(container.querySelectorAll(".MuiSkeleton-root").length).toBeGreaterThan(0);
    expect(screen.getByTestId("search-slot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "new_project" })).toBeInTheDocument();
  });

  it("welcomes an established caller back, keeping the search slot and quick actions", () => {
    renderHero({ stage: "established" });

    expect(screen.getByText("welcome_back")).toBeInTheDocument();
    expect(screen.getByTestId("search-slot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "new_project" })).toBeInTheDocument();
  });

  it("hides the help strip once established", () => {
    renderHero({ stage: "established", showHelp: false });

    expect(screen.queryByText("help_getting_started")).not.toBeInTheDocument();
    expect(screen.queryByText("help_docs")).not.toBeInTheDocument();
    expect(screen.queryByText("help_video")).not.toBeInTheDocument();
  });

  it("shows the help strip in New and Getting started", () => {
    renderHero({ stage: "new", showHelp: true });

    expect(screen.getByText("help_getting_started")).toBeInTheDocument();
    expect(screen.getByText("help_docs")).toBeInTheDocument();
    expect(screen.getByText("help_video")).toBeInTheDocument();
  });

  it("points the help tiles at the quickstart guide, the docs home and the catchment video", () => {
    renderHero({ stage: "new", showHelp: true });

    const href = (name: RegExp) => screen.getByRole("link", { name }).getAttribute("href");

    expect(href(/help_getting_started/)).toBe(
      "https://goat.plan4better.de/docs/getting_started/quickstart_guide"
    );
    expect(href(/help_docs/)).toBe("https://goat.plan4better.de/docs");
    expect(href(/help_video/)).toBe("https://www.youtube.com/watch?v=_clsR386b9w");
  });
});
