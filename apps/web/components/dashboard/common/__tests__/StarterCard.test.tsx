import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { tagColor } from "@/lib/utils/tagColor";
import type { TemplateRead } from "@/lib/validations/template";

import StarterCard from "@/components/dashboard/common/StarterCard";

const { useUserProfileMock } = vi.hoisted(() => ({ useUserProfileMock: vi.fn() }));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => (opts ? `${key}:${JSON.stringify(opts)}` : key),
  }),
}));

vi.mock("@/i18n/utils", () => ({ useDateFnsLocale: () => undefined }));
vi.mock("@/lib/api/users", () => ({ useUserProfile: useUserProfileMock }));

vi.mock("@/components/dashboard/common/KindBadges", () => ({
  default: ({ kinds }: { kinds: string[] }) => <div data-testid="kind-badges">{JSON.stringify(kinds)}</div>,
}));

useUserProfileMock.mockReturnValue({
  userProfile: { id: "u-me", firstname: "Marie", lastname: "Klein", avatar: "" },
});

const template = (overrides: Partial<TemplateRead>): TemplateRead => ({
  id: "t1",
  name: "Bus network analysis",
  description: null,
  categories: [],
  thumbnail_url: null,
  space_id: "s1",
  folder_id: "f1",
  created_by: null,
  payload_kind: "workflow",
  kinds: ["workflow"],
  inputs: [],
  ships_data: false,
  catalog_status: "published",
  source_ref: {},
  datasets_needing_share: [],
  my_role: "viewer",
  created_at: new Date().toISOString(),
  updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
  ...overrides,
});

describe("StarterCard", () => {
  it("opens the template on click", () => {
    const onOpen = vi.fn();
    render(<StarterCard template={template({})} onOpen={onOpen} />);

    fireEvent.click(screen.getByText("Bus network analysis"));

    expect(onOpen).toHaveBeenCalled();
  });

  it("shows the creator, the last-updated time and the first category in one meta row", () => {
    render(
      <StarterCard
        template={template({
          created_by: { id: "u1", name: "Marco Albrecht", avatar: null },
          categories: ["Mobility"],
        })}
        onOpen={vi.fn()}
      />
    );

    const creator = screen.getByText("Marco Albrecht");
    const time = screen.getByText("3 hours ago");
    const category = screen.getByText("Mobility");
    expect(creator).toBeInTheDocument();
    // One row carries all three: the creator cell, the time and the category
    // tag, the last pushed to the right where a content card puts its
    // audience chip.
    const metaRow = time.parentElement!;
    expect(metaRow).toContainElement(creator);
    expect(metaRow).toContainElement(category);
  });

  it("renders no tag row under the meta row", () => {
    render(
      <StarterCard
        template={template({
          created_by: { id: "u1", name: "Marco Albrecht", avatar: null },
          categories: ["Mobility", "Transit"],
        })}
        onOpen={vi.fn()}
      />
    );

    // The name's row and the meta row are all the paper carries.
    const metaRow = screen.getByText("3 hours ago").parentElement!;
    expect(metaRow.nextElementSibling).toBeNull();
  });

  it("holds the same title row height as a content card, so both cards line up", () => {
    const { rerender } = render(<StarterCard template={template({})} onOpen={vi.fn()} />);

    // `ContentCard`'s title row is as tall as its kebab: 28px, 40px on a phone.
    expect(screen.getByText("Bus network analysis").parentElement).toHaveStyle({ minHeight: "28px" });

    rerender(<StarterCard template={template({})} onOpen={vi.fn()} mobile />);

    expect(screen.getByText("Bus network analysis").parentElement).toHaveStyle({ minHeight: "40px" });
  });

  it("keeps the kind on the badge and out of the body text", () => {
    render(
      <StarterCard
        template={template({
          kinds: ["workflow", "dashboard"],
          created_by: { id: "u1", name: "Marco Albrecht", avatar: null },
        })}
        onOpen={vi.fn()}
      />
    );

    expect(screen.getByTestId("kind-badges")).toHaveTextContent('["workflow","dashboard"]');
    expect(screen.queryByText(/template_kind_/)).not.toBeInTheDocument();
  });

  it("falls back to GOAT, mark and name, when there is no creating account", () => {
    const { unmount } = render(<StarterCard template={template({ created_by: null })} onOpen={vi.fn()} />);

    expect(screen.getByText("source_goat")).toBeInTheDocument();
    expect(screen.getByTestId("template-source-avatar")).toBeInTheDocument();
    expect(screen.getByText("3 hours ago")).toBeInTheDocument();
    // The stand-in sits in the avatar's own slot, so the row is built the
    // same way whether or not a person made the template.
    const sourceRow = screen.getByText("source_goat").parentElement!;
    expect(sourceRow).toContainElement(screen.getByTestId("template-source-avatar"));
    const sourceMetaRow = screen.getByText("3 hours ago").parentElement!;
    const sourceCells = sourceMetaRow.children.length;
    unmount();

    render(
      <StarterCard
        template={template({ created_by: { id: "u1", name: "Marco Albrecht", avatar: null } })}
        onOpen={vi.fn()}
      />
    );

    // A creator keeps their own avatar — initials on the colour their id
    // hashes to — and no GOAT mark.
    expect(screen.getByText("MA")).toBeInTheDocument();
    expect(screen.queryByTestId("template-source-avatar")).not.toBeInTheDocument();
    expect(screen.getByText("3 hours ago").parentElement!.children.length).toBe(sourceCells);
  });

  it("shows the sample data badge only when the template ships one", () => {
    const { rerender } = render(
      <StarterCard template={template({ ships_data: false })} onOpen={vi.fn()} />
    );
    expect(screen.queryByText("includes_data")).not.toBeInTheDocument();

    rerender(<StarterCard template={template({ ships_data: true })} onOpen={vi.fn()} />);
    expect(screen.getByText("includes_data")).toBeInTheDocument();
  });

  it("marks the band's bottom-left corner with the page, or with sample data", () => {
    const { rerender } = render(
      <StarterCard
        template={template({ payload_kind: "layout", page_size: "A3", page_orientation: "landscape" })}
        onOpen={vi.fn()}
      />
    );

    // The orientation goes through `t`, which the mock echoes with its options.
    expect(screen.getByText(/^A3 · landscape/).parentElement).toHaveStyle({
      bottom: "8px",
      left: "8px",
    });

    // A workflow's shipped sample data takes the same corner: only one of the
    // two can ever apply to one template.
    rerender(<StarterCard template={template({ ships_data: true })} onOpen={vi.fn()} />);

    expect(screen.getByText("includes_data").parentElement).toHaveStyle({ bottom: "8px", left: "8px" });
    expect(screen.queryByText(/·/)).not.toBeInTheDocument();
  });

  it("offers the tag and the bare count as two renderings the card's width picks between", () => {
    render(
      <StarterCard
        template={template({ categories: ["Mobility", "Bicycle", "Accessibility"] })}
        onOpen={vi.fn()}
      />
    );

    // Which one is on screen is a container query on the card — jsdom has no
    // layout, so what is asserted here is that both renderings exist and
    // carry the right content: the wide one spells a category out, the narrow
    // one is the count of all of them and is hidden from assistive tech.
    const wide = screen.getByTestId("template-category-tags");
    const narrow = screen.getByTestId("template-category-count");
    expect(wide).toContainElement(screen.getByText("Mobility"));
    expect(wide).toContainElement(screen.getByText("+2"));
    expect(narrow).toContainElement(screen.getByText("+3"));
    expect(narrow.getAttribute("aria-hidden")).toBe("true");
    // Their widths and which one is on screen are container-query CSS, which
    // jsdom neither parses nor lays out — that half is checked in the browser
    // (see the report's measurements).
  });

  it("gives the creator's name a floor so a category can never squeeze it out", () => {
    render(
      <StarterCard
        template={template({
          created_by: { id: "u1", name: "Marco Albrecht", avatar: null },
          categories: ["Mobility"],
        })}
        onOpen={vi.fn()}
      />
    );

    // 22px avatar + 7px gap + 56px of name: the cell shrinks with the row but
    // never past this, so the name reads at the Home band's 210px card.
    expect(screen.getByText("Marco Albrecht").parentElement).toHaveStyle({ minWidth: "85px" });
    // The time is never shrunk at all.
    expect(screen.getByText("3 hours ago")).toHaveStyle({ flexShrink: 0 });
  });

  it("renders no category rendering at all for a template with none", () => {
    render(<StarterCard template={template({ categories: [] })} onOpen={vi.fn()} />);

    expect(screen.queryByTestId("template-category-tags")).not.toBeInTheDocument();
    expect(screen.queryByTestId("template-category-count")).not.toBeInTheDocument();
  });

  it("shows the first category plus a +n overflow marker naming the rest", () => {
    render(
      <StarterCard
        template={template({ categories: ["Mobility", "Bicycle", "Accessibility"] })}
        onOpen={vi.fn()}
      />
    );

    expect(screen.getByText("Mobility")).toBeInTheDocument();
    expect(screen.queryByText("Bicycle")).not.toBeInTheDocument();
    expect(screen.queryByText("Accessibility")).not.toBeInTheDocument();
    const overflow = screen.getByText("+2");
    expect(overflow).toBeInTheDocument();
    // The tooltip names the categories the meta row has no room for.
    expect(overflow.parentElement?.getAttribute("aria-label")).toBe("Bicycle, Accessibility");
    // The time reads in full beside them.
    expect(screen.getByText("3 hours ago")).toHaveStyle({ flexShrink: 0 });
  });

  it("ellipsises a long category and keeps its full name in the tag's title", () => {
    render(
      <StarterCard
        template={template({ categories: ["Sustainable Urban Mobility Planning"] })}
        onOpen={vi.fn()}
      />
    );

    const tag = screen.getByText("Sustainable Urban Mobility Planning");
    // The cap is on the tag's own box; the ellipsis is the tag's.
    expect(tag.parentElement).toHaveStyle({ maxWidth: "90px" });
    expect(tag).toHaveStyle({ overflow: "hidden", textOverflow: "ellipsis" });
    expect(tag.getAttribute("title")).toBe("Sustainable Urban Mobility Planning");
    expect(screen.getByText("3 hours ago")).toHaveStyle({ flexShrink: 0 });
  });

  it("drops the visible tag on a phone and counts the categories instead", () => {
    render(
      <StarterCard
        template={template({ categories: ["Mobility", "Bicycle", "Accessibility"] })}
        onOpen={vi.fn()}
        mobile
      />
    );

    expect(screen.queryByText("Mobility")).not.toBeInTheDocument();
    // One rendering only on a phone: the count, shown by the same container
    // query as on a wider screen, so a narrow grid cell drops it instead of
    // pushing it past the card's edge.
    expect(screen.queryByTestId("template-category-tags")).not.toBeInTheDocument();
    const count = screen.getByTestId("template-category-count");
    expect(count.getAttribute("aria-hidden")).toBeNull();
    const marker = screen.getByText("+3");
    expect(count).toContainElement(marker);
    expect(marker.parentElement?.getAttribute("aria-label")).toBe("Mobility, Bicycle, Accessibility");
    expect(screen.getByText("3 hours ago")).toHaveStyle({ flexShrink: 0 });
  });

  it("calls onTogglePin without opening the template", () => {
    const onOpen = vi.fn();
    const onTogglePin = vi.fn();
    render(<StarterCard template={template({})} onOpen={onOpen} pinned={false} onTogglePin={onTogglePin} />);

    fireEvent.click(screen.getByRole("button", { name: "pin_to_home" }));

    expect(onTogglePin).toHaveBeenCalled();
    expect(onOpen).not.toHaveBeenCalled();
  });

  it("labels the pin button unpin_from_home once pinned", () => {
    render(<StarterCard template={template({})} onOpen={vi.fn()} pinned onTogglePin={vi.fn()} />);

    expect(screen.getByRole("button", { name: "unpin_from_home" })).toBeInTheDocument();
  });

  it("colours the shown category tag by its own name", () => {
    const { rerender } = render(
      <StarterCard template={template({ categories: ["Mobility"] })} onOpen={vi.fn()} />
    );

    expect(screen.getByText("Mobility")).toHaveStyle({ color: tagColor("Mobility").fg });

    rerender(<StarterCard template={template({ categories: ["Transit"] })} onOpen={vi.fn()} />);

    expect(screen.getByText("Transit")).toHaveStyle({ color: tagColor("Transit").fg });
  });

  it("tags a layout template with its page on the thumbnail band, not beside the categories", () => {
    render(
      <StarterCard
        template={template({
          payload_kind: "layout",
          page_size: "A3",
          page_orientation: "landscape",
          categories: ["Mobility"],
        })}
        onOpen={vi.fn()}
      />
    );

    // The orientation goes through `t`, which the mock echoes with its options.
    const page = screen.getByText(/^A3 · landscape/);
    // The kind badge sits in its own overlay on the band, so two steps up
    // from it is the band itself.
    const band = screen.getByTestId("kind-badges").parentElement!.parentElement!;
    expect(band).toContainElement(page);
    // The category tag rides in the meta row, not on the band.
    expect(band).not.toContainElement(screen.getByText("Mobility"));
  });

  it("renders no overflow chip when there are no categories", () => {
    render(<StarterCard template={template({ categories: [] })} onOpen={vi.fn()} />);
    expect(screen.queryByText(/^\+/)).not.toBeInTheDocument();
  });

  it("shows the template's own thumbnail when it has one", () => {
    const { container } = render(
      <StarterCard
        template={template({ thumbnail_url: "https://example.test/thumb.png" })}
        onOpen={vi.fn()}
      />
    );

    expect(container.querySelector("img")?.getAttribute("src")).toBe("https://example.test/thumb.png");
    // The picture is the image, so the kind's mark is not drawn behind it.
    expect(screen.queryByTestId("content-thumbnail-mark")).not.toBeInTheDocument();
    expect(screen.getByTestId("kind-badges")).toHaveTextContent('["workflow"]');
  });

  it("draws the payload's own default when there is no thumbnail", () => {
    const { rerender } = render(
      <StarterCard template={template({ thumbnail_url: null })} onOpen={vi.fn()} />
    );

    // A workflow reads as a chain of steps.
    expect(screen.getByTestId("template-default-workflow")).toBeInTheDocument();
    expect(screen.queryByTestId("content-thumbnail-mark")).not.toBeInTheDocument();
    expect(screen.getByTestId("kind-badges")).toHaveTextContent('["workflow"]');

    // A layout reads as the page it prints on, in that page's orientation.
    rerender(
      <StarterCard
        template={template({
          thumbnail_url: null,
          payload_kind: "layout",
          kinds: ["layout"],
          page_size: "A4",
          page_orientation: "landscape",
        })}
        onOpen={vi.fn()}
      />
    );

    expect(screen.getByTestId("template-preview-page").getAttribute("data-orientation")).toBe("landscape");
  });

  it("shows the template mark for a project payload, like every other content card", () => {
    render(
      <StarterCard
        template={template({ thumbnail_url: null, payload_kind: "project", kinds: [] })}
        onOpen={vi.fn()}
      />
    );

    expect(screen.getByTestId("content-thumbnail-mark")).toBeInTheDocument();
    expect(screen.queryByTestId("template-default-workflow")).not.toBeInTheDocument();
  });

  it("falls back to the payload's default when the thumbnail fails to load", () => {
    const { container } = render(
      <StarterCard template={template({ thumbnail_url: "https://example.test/gone.png" })} onOpen={vi.fn()} />
    );

    fireEvent.error(container.querySelector("img")!);

    expect(container.querySelector("img")).not.toBeInTheDocument();
    expect(screen.getByTestId("template-default-workflow")).toBeInTheDocument();
  });

  it("keeps the thumbnail band at 132px, and at 96px on a phone", () => {
    const withThumbnail = template({ thumbnail_url: "https://example.test/thumb.png" });
    const { container, rerender } = render(<StarterCard template={withThumbnail} onOpen={vi.fn()} />);

    expect(container.querySelector("img")?.parentElement).toHaveStyle({ height: "132px" });

    rerender(<StarterCard template={withThumbnail} onOpen={vi.fn()} mobile />);

    expect(container.querySelector("img")?.parentElement).toHaveStyle({ height: "96px" });
  });
});
