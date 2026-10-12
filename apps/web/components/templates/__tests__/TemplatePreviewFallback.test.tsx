import { render, screen } from "@testing-library/react";
import { afterAll, describe, expect, it, vi } from "vitest";

import type { TemplatePreviewDescriptor } from "@/lib/validations/template";

import TemplatePreviewFallback from "@/components/templates/TemplatePreviewFallback";

// The static basemap frame is drawn only with a MapTiler key, read when the
// constants module is first evaluated.
vi.hoisted(() => {
  vi.stubEnv("NEXT_PUBLIC_MAPTILER_KEY", "test-key");
});
afterAll(() => {
  vi.unstubAllEnvs();
});

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => (opts ? `${key}:${JSON.stringify(opts)}` : key),
  }),
}));

const workflowPreview = (labels: string[]): TemplatePreviewDescriptor => ({
  kind: "workflow",
  nodes: labels.map((label, index) => ({
    label,
    type: index === 0 ? "dataset" : "tool",
    x: index * 320,
    y: 0,
    w: 220,
    h: 92,
  })),
  edges: labels.slice(1).map((_unused, index): [number, number] => [index, index + 1]),
});

describe("TemplatePreviewFallback", () => {
  it("draws a node per descriptor node and a path per edge", () => {
    render(
      <TemplatePreviewFallback
        descriptor={workflowPreview(["Stops", "Buffer", "Save"])}
        payloadKind="workflow"
      />
    );

    const nodes = screen.getAllByTestId("template-preview-node");
    expect(nodes).toHaveLength(3);
    expect(nodes.map((node) => node.getAttribute("data-type"))).toEqual(["dataset", "tool", "tool"]);
    expect(screen.getAllByTestId("template-preview-edge")).toHaveLength(2);
    expect(screen.getByText("Stops")).toBeInTheDocument();
    expect(screen.getByText("Buffer")).toBeInTheDocument();
  });

  it("draws each node with the icon and handles its canvas node carries", () => {
    const { container } = render(
      <TemplatePreviewFallback
        payloadKind="workflow"
        descriptor={{
          kind: "workflow",
          nodes: [
            { label: "Stops", type: "dataset", x: 0, y: 0, w: 220, h: 92, icon: "point" },
            { label: "Buffer", type: "tool", x: 320, y: 0, w: 220, h: 92, icon: "buffer" },
          ],
          edges: [[0, 1]],
        }}
      />
    );

    // The drawing's own root svg plus one nested icon svg per node.
    expect(container.querySelectorAll("svg")).toHaveLength(3);
    // Each glyph is placed and sized by the drawing rather than by the class
    // MUI would apply (`width: 1em`), and carries the tool-icon tones a
    // two-tone glyph reads its own colours off.
    const glyph = container.querySelector("svg svg") as SVGElement;
    expect(glyph.getAttribute("x")).not.toBeNull();
    expect(glyph.style.width.endsWith("px")).toBe(true);
    expect(glyph.style.getPropertyValue("--icon-color-1")).toBe("#666666");
    // A dataset's one source handle, and the tool's target and source.
    const nodes = screen.getAllByTestId("template-preview-node");
    expect(nodes[0].querySelectorAll("circle")).toHaveLength(1);
    expect(nodes[1].querySelectorAll("circle")).toHaveLength(2);
  });

  it("takes the node title the canvas writes, through the reader's own translator", () => {
    render(
      <TemplatePreviewFallback
        payloadKind="workflow"
        descriptor={{
          kind: "workflow",
          nodes: [{ label: "buffer_v2", type: "tool", x: 0, y: 0, w: 320, h: 92, icon: "buffer" }],
          edges: [],
        }}
      />
    );

    // The mocked `t` echoes its key, which is the process id — the label
    // stored beside it is not what the canvas writes.
    expect(screen.getByText(/^buffer/)).toBeInTheDocument();
    expect(screen.queryByText("buffer_v2")).not.toBeInTheDocument();
  });

  it("draws no chain placeholder once it has a descriptor to draw", () => {
    render(<TemplatePreviewFallback descriptor={workflowPreview(["Stops"])} payloadKind="workflow" />);

    expect(screen.queryByTestId("template-preview-step")).not.toBeInTheDocument();
  });

  it("draws a layout's page in its own orientation with its element boxes", () => {
    render(
      <TemplatePreviewFallback
        payloadKind="layout"
        descriptor={{
          kind: "layout",
          orientation: "landscape",
          page: { width: 297, height: 210 },
          elements: [
            { type: "map", x: 10, y: 10, width: 200, height: 150 },
            { type: "text", x: 220, y: 10, width: 60, height: 40 },
          ],
        }}
      />
    );

    // Read the attribute off the DOM rather than through `toHaveAttribute`:
    // the repo's ESLint setup reads that jest-dom matcher as Playwright's
    // (async) matcher of the same name.
    expect(screen.getByTestId("template-preview-page").getAttribute("data-orientation")).toBe("landscape");
    const elements = screen.getAllByTestId("template-preview-element");
    expect(elements).toHaveLength(2);
    expect(elements.map((element) => element.getAttribute("data-type"))).toEqual(["map", "text"]);
    // Each block carries the placeholder glyph for what it is, rather than
    // an empty outline: the map its land and roads, the text its lines.
    expect(elements[0].querySelectorAll("path").length).toBeGreaterThan(0);
    expect(elements[0].querySelectorAll("line")).toHaveLength(2);
    // The four text lines, and no outline: a layout element frames itself
    // only where its own style says so.
    expect(elements[1].querySelectorAll("rect")).toHaveLength(4);
  });

  it("frames and fills a layout block only where the block asks for it", () => {
    render(
      <TemplatePreviewFallback
        payloadKind="layout"
        descriptor={{
          kind: "layout",
          orientation: "landscape",
          page: { width: 297, height: 210 },
          elements: [
            { type: "table", x: 10, y: 10, width: 100, height: 60 },
            {
              type: "table",
              x: 10,
              y: 80,
              width: 100,
              height: 60,
              style: {
                border: { color: "#1A73E8", width: 1 },
                background: { color: "#FFF3CD", opacity: 0.4 },
                opacity: 0.8,
              },
            },
          ],
        }}
      />
    );

    const [bare, styled] = screen.getAllByTestId("template-preview-element");
    // The bare block shows its content glyph and nothing around it.
    expect(bare.querySelectorAll('rect[fill="none"]')).toHaveLength(0);
    expect(bare.querySelectorAll("line").length).toBeGreaterThan(0);
    // The styled one carries its own frame, its own ground and its opacity.
    const frame = styled.querySelector('rect[fill="none"]');
    expect(frame?.getAttribute("stroke")).toBe("#1A73E8");
    expect(Number(frame?.getAttribute("stroke-width"))).toBeGreaterThan(1);
    const ground = styled.querySelector('rect[fill="#FFF3CD"]');
    expect(ground?.getAttribute("fill-opacity")).toBe("0.4");
    expect(styled.getAttribute("opacity")).toBe("0.8");
  });

  it("draws a layout's real text, its legend title and its basemap frame", () => {
    render(
      <TemplatePreviewFallback
        payloadKind="layout"
        descriptor={{
          kind: "layout",
          orientation: "landscape",
          page: { width: 297, height: 210 },
          elements: [
            {
              type: "map",
              x: 10,
              y: 30,
              width: 200,
              height: 150,
              viewState: { latitude: 48.1374, longitude: 11.5755, zoom: 11.5 },
            },
            {
              type: "text",
              x: 10,
              y: 8,
              width: 200,
              height: 18,
              html: "<p><strong>Ridership 2026</strong></p>",
              fontSize: 32,
            },
            { type: "legend", x: 220, y: 30, width: 60, height: 60, title: "Stops per hour" },
          ],
        }}
      />
    );

    // The scaffold is live DOM, so the basemap is referenced by url rather
    // than inlined the way the stored PNG needs it.
    const basemap = screen.getByTestId("template-preview-basemap");
    expect(basemap.getAttribute("href")).toContain(
      "https://api.maptiler.com/maps/streets-v2/static/11.5755,48.1374,11.5/"
    );
    const prose = screen.getByTestId("template-preview-prose");
    expect(prose.querySelector("strong")?.textContent).toBe("Ridership 2026");
    expect(screen.getByTestId("template-preview-element-title").textContent).toBe("Stops per hour");
  });

  it("draws a block it knows no glyph for as its outline alone", () => {
    render(
      <TemplatePreviewFallback
        payloadKind="layout"
        descriptor={{
          kind: "layout",
          orientation: "portrait",
          page: { width: 210, height: 297 },
          elements: [{ type: "something_new", x: 10, y: 10, width: 100, height: 40 }],
        }}
      />
    );

    const element = screen.getByTestId("template-preview-element");
    expect(element.querySelectorAll("rect")).toHaveLength(1);
    expect(element.querySelectorAll("path, line, circle")).toHaveLength(0);
  });

  it("draws the neutral placeholder chain for a workflow with no descriptor", () => {
    render(<TemplatePreviewFallback descriptor={null} payloadKind="workflow" />);

    const steps = screen.getAllByTestId("template-preview-step");
    expect(steps).toHaveLength(3);
    expect(steps.every((step) => step.textContent === "")).toBe(true);
    expect(screen.queryByTestId("template-preview-node")).not.toBeInTheDocument();
  });

  it("draws the placeholder for a descriptor whose shape it does not know", () => {
    render(
      <TemplatePreviewFallback
        payloadKind="workflow"
        descriptor={{ kind: "builder", widgets: 3 } as unknown as TemplatePreviewDescriptor}
      />
    );

    expect(screen.getAllByTestId("template-preview-step")).toHaveLength(3);
  });

  it("draws a portrait page for a layout with no descriptor", () => {
    render(<TemplatePreviewFallback descriptor={null} payloadKind="layout" />);

    expect(screen.getByTestId("template-preview-page").getAttribute("data-orientation")).toBe("portrait");
    expect(screen.queryByTestId("template-preview-element")).not.toBeInTheDocument();
  });

  it("draws an annotation's own rich text in the note, in the note's own colour", () => {
    const html = '<h2>Step one</h2><p>Buffer the <span style="color: #4C9F70">stops</span></p>';
    const annotation: TemplatePreviewDescriptor = {
      kind: "workflow",
      nodes: [
        {
          label: "textAnnotation",
          type: "textAnnotation",
          x: 0,
          y: 0,
          w: 400,
          h: 200,
          color: "#4C9F70",
          html,
        },
      ],
      edges: [],
    };

    const { container } = render(<TemplatePreviewFallback descriptor={annotation} payloadKind="workflow" />);

    const note = screen.getByTestId("template-preview-note");
    // The markup itself: the heading and the coloured run, not a flattening.
    expect(note.querySelector("h2")?.textContent).toBe("Step one");
    expect(note.querySelector("span")?.getAttribute("style")).toContain("#4C9F70");
    // The card is painted in the note's own colour, not the default tint.
    const card = container.querySelector('[data-type="textAnnotation"] rect');
    expect(card?.getAttribute("fill")).toBe("#4C9F70");
    expect(card?.getAttribute("stroke")).toBe("#4C9F70");
  });

  it("draws an untexted note card for an annotation with no markup", () => {
    const annotation: TemplatePreviewDescriptor = {
      kind: "workflow",
      nodes: [{ label: "textAnnotation", type: "textAnnotation", x: 0, y: 0, w: 400, h: 200 }],
      edges: [],
    };

    render(<TemplatePreviewFallback descriptor={annotation} payloadKind="workflow" />);

    expect(screen.getByTestId("template-preview-node")).toBeInTheDocument();
    expect(screen.queryByTestId("template-preview-note")).not.toBeInTheDocument();
  });

  it("draws a project as its own mark", () => {
    render(<TemplatePreviewFallback descriptor={null} payloadKind="project" />);

    expect(screen.getByTestId("template-preview-project")).toBeInTheDocument();
    expect(screen.queryByTestId("template-preview-node")).not.toBeInTheDocument();
    expect(screen.queryByTestId("template-preview-step")).not.toBeInTheDocument();
  });
});
