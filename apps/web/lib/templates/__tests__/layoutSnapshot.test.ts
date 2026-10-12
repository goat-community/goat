import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { layoutDrawing } from "@/lib/templates/layoutDrawing";
import { LAYOUT_SNAPSHOT_PALETTE, renderLayoutSnapshot, svgForLayout } from "@/lib/templates/layoutSnapshot";
import { SCAFFOLD_FRAME, SNAPSHOT_SIZE } from "@/lib/templates/previewGeometry";
import { STATIC_MAP_TIMEOUT, clearStaticMapCache } from "@/lib/templates/staticMap";
import type { TemplateLayoutPreview } from "@/lib/validations/template";

// The static basemap frame is drawn only with a MapTiler key, read when the
// constants module is first evaluated.
vi.hoisted(() => {
  vi.stubEnv("NEXT_PUBLIC_MAPTILER_KEY", "test-key");
});
afterAll(() => {
  vi.unstubAllEnvs();
});

const descriptor: TemplateLayoutPreview = {
  kind: "layout",
  orientation: "landscape",
  page: { width: 297, height: 210 },
  elements: [
    { type: "map", x: 10, y: 10, width: 200, height: 150 },
    { type: "legend", x: 220, y: 10, width: 60, height: 50 },
    { type: "scalebar", x: 220, y: 70, width: 60, height: 10 },
  ],
};

const portrait: TemplateLayoutPreview = {
  kind: "layout",
  orientation: "portrait",
  page: { width: 210, height: 297 },
  elements: [{ type: "map", x: 10, y: 10, width: 190, height: 200 }],
};

/** Every positioned rect in the drawing, as `[x, y, w, h]` — the page and the
 * element outlines, not the full-frame ground. */
const positionedRects = (svg: string): number[][] =>
  [...svg.matchAll(/<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g)].map((match) =>
    match.slice(1).map(Number)
  );

/** An `Image` whose `src` setter reports the outcome the test asked for, so
 * the rasterising path can run in jsdom — which never loads an SVG data URL
 * on its own. */
const stubImage = (outcome: "load" | "error") => {
  class StubImage {
    onload: (() => void) | null = null;
    onerror: (() => void) | null = null;
    set src(_value: string) {
      setTimeout(() => (outcome === "load" ? this.onload?.() : this.onerror?.()), 0);
    }
  }
  vi.stubGlobal("Image", StubImage);
};

/** A canvas that hands back a 2D context and, on `toBlob`, whatever this
 * test wants of it. */
const stubCanvas = (blob: Blob | null) => {
  const context = { fillStyle: "", fillRect: vi.fn(), drawImage: vi.fn() };
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(
    context as unknown as CanvasRenderingContext2D
  );
  HTMLCanvasElement.prototype.toBlob = function toBlob(callback: BlobCallback) {
    callback(blob);
  };
  return context;
};

/** A layout whose blocks carry their own content: a map frame with a camera
 * on it, a title, and a named legend. */
const withContent: TemplateLayoutPreview = {
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
      html: '<p style="text-align: center"><strong>Ridership 2026</strong></p>',
      fontSize: 32,
    },
    { type: "legend", x: 220, y: 30, width: 60, height: 60, title: "Stops per hour" },
  ],
};

/** The bytes of a PNG, as the static endpoint would answer with them. */
const pngBlob = (): Blob => new Blob([new Uint8Array([137, 80, 78, 71, 13, 10])], { type: "image/png" });

/** A `fetch` that answers every request the way this test wants: with a PNG,
 * with a refusal, or never — until the request is abandoned. */
const stubFetch = (outcome: "png" | "status" | "network" | "hang") => {
  const fetchMock = vi.fn((_url: string, init?: { signal?: AbortSignal }) => {
    if (outcome === "png") return Promise.resolve({ ok: true, blob: () => Promise.resolve(pngBlob()) });
    if (outcome === "status") return Promise.resolve({ ok: false, blob: () => Promise.resolve(pngBlob()) });
    if (outcome === "network") return Promise.reject(new Error("offline"));
    return new Promise((_resolve, reject) => {
      init?.signal?.addEventListener("abort", () => reject(new Error("aborted")));
    });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  vi.useRealTimers();
  clearStaticMapCache();
});

describe("svgForLayout", () => {
  it("draws the page as white paper on a light ground, at the snapshot's own size", async () => {
    const svg = await svgForLayout(descriptor);

    expect(svg.startsWith("<svg xmlns=")).toBe(true);
    expect(svg).toContain(`width="${SNAPSHOT_SIZE.width}"`);
    expect(svg).toContain(`height="${SNAPSHOT_SIZE.height}"`);
    expect(svg).toContain(`viewBox="0 0 ${SNAPSHOT_SIZE.width} ${SNAPSHOT_SIZE.height}"`);
    // The ground fills the frame; the paper is a rect placed on it.
    expect(svg).toContain(
      `<rect width="${SNAPSHOT_SIZE.width}" height="${SNAPSHOT_SIZE.height}" fill="${LAYOUT_SNAPSHOT_PALETTE.ground}" />`
    );
    expect(svg).toContain(`fill="${LAYOUT_SNAPSHOT_PALETTE.page}"`);
    expect(svg).toContain(`stroke="${LAYOUT_SNAPSHOT_PALETTE.pageBorder}"`);
    // The paper carries a soft shadow, defined in this document.
    expect(svg).toContain("<feDropShadow");
    expect(svg).toMatch(/filter="url\(#goat-layout-shadow-\d+\)"/);
  });

  it("fits the page into the frame and centres it, leaving a portrait page its margins", async () => {
    const landscapePage = positionedRects(await svgForLayout(descriptor))[0];
    const portraitPage = positionedRects(await svgForLayout(portrait))[0];

    // Both pages are `meet`-fitted, so each keeps its own aspect ratio and
    // is centred on what is left of the frame.
    for (const [x, y, w, h] of [landscapePage, portraitPage]) {
      expect(w).toBeLessThanOrEqual(SNAPSHOT_SIZE.width);
      expect(h).toBeLessThanOrEqual(SNAPSHOT_SIZE.height);
      expect(Math.abs(x + w / 2 - SNAPSHOT_SIZE.width / 2)).toBeLessThan(1);
      expect(Math.abs(y + h / 2 - SNAPSHOT_SIZE.height / 2)).toBeLessThan(1);
    }
    // A portrait page is height-bound, so it leaves wide margins — that is
    // the picture, not a fault.
    expect(portraitPage[2] / portraitPage[3]).toBeCloseTo(210 / 297, 2);
    expect(portraitPage[0]).toBeGreaterThan(SNAPSHOT_SIZE.width * 0.25);
    expect(landscapePage[2] / landscapePage[3]).toBeCloseTo(297 / 210, 2);
  });

  it("draws one group per element, in the light palette", async () => {
    const svg = await svgForLayout(descriptor);

    const groups = [...svg.matchAll(/<g data-type="([^"]+)"/g)].map((match) => match[1]);
    expect(groups).toEqual(["map", "legend", "scalebar"]);
    // The glyphs themselves: the map's land in the tint on its wash, its
    // roads and the legend's rows in the line tone.
    expect(svg).toContain(`fill="${LAYOUT_SNAPSHOT_PALETTE.glyph.tint}"`);
    expect(svg).toContain(`fill="${LAYOUT_SNAPSHOT_PALETTE.glyph.wash}"`);
    expect(svg).toContain(`stroke="${LAYOUT_SNAPSHOT_PALETTE.glyph.line}"`);
    // Nothing is drawn in a theme-dependent value.
    expect(svg).not.toContain("var(--");
    expect(svg).not.toContain("rgba(");
  });

  it("draws each element's glyph as the primitives the scaffold draws", async () => {
    const svg = await svgForLayout(descriptor);
    const drawing = layoutDrawing(descriptor, { size: SNAPSHOT_SIZE });

    // Every shape the shared drawing carries is written out: the map's
    // paths and roads, the legend's swatches, the scalebar's segments.
    const glyphs = drawing.elements.flatMap((element) => element.glyphs);
    expect(glyphs.length).toBeGreaterThan(10);
    expect((svg.match(/<path /g) ?? []).length).toBe(glyphs.filter((shape) => shape.shape === "path").length);
    expect((svg.match(/<line /g) ?? []).length).toBe(glyphs.filter((shape) => shape.shape === "line").length);
  });

  it("draws a block it knows no glyph for as its outline alone", async () => {
    const svg = await svgForLayout({
      kind: "layout",
      orientation: "portrait",
      page: { width: 210, height: 297 },
      elements: [{ type: "something_new", x: 10, y: 10, width: 100, height: 40 }],
    });

    expect(svg).toContain('<g data-type="something_new">');
    expect(svg).not.toContain("<path ");
    expect(svg).not.toContain("<line ");
    expect(svg).not.toContain("<circle ");
  });

  it("draws an elementless layout as the bare page", async () => {
    const svg = await svgForLayout({
      kind: "layout",
      orientation: "portrait",
      page: { width: 210, height: 297 },
      elements: [],
    });

    expect(svg).not.toContain("<g ");
    expect(positionedRects(svg)).toHaveLength(1);
  });

  it("is self-contained for a layout carrying no content of its own", async () => {
    const svg = await svgForLayout(descriptor);

    expect(svg).not.toContain("foreignObject");
    expect(svg).not.toContain("<text");
    expect(svg).not.toContain("font-family");
    expect(svg).not.toContain("@import");
    expect(svg).not.toContain("<image");
    expect(svg.replace('xmlns="http://www.w3.org/2000/svg"', "")).not.toContain("http");
    // Every url() names something this document defines, suffixed per
    // drawing so two on one page cannot take each other's.
    const references = [...svg.matchAll(/url\(#([^)]+)\)/g)].map((match) => match[1]);
    expect(references.length).toBeGreaterThan(0);
    for (const id of new Set(references)) {
      expect(id).toMatch(/^goat-layout-shadow-\d+$/);
      expect(svg).toContain(`id="${id}"`);
    }
  });

  it("inlines the basemap frame the static endpoint answers with", async () => {
    const fetchMock = stubFetch("png");

    const svg = await svgForLayout(withContent);

    // One request, at the element's own camera and pixel aspect, in the
    // style the app's default basemap names.
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url] = fetchMock.mock.calls[0];
    expect(url).toMatch(
      /^https:\/\/api\.maptiler\.com\/maps\/streets-v2\/static\/11\.5755,48\.1374,11\.5\/\d+x\d+@2x\.png\?key=/
    );
    // The watermark is suppressed: a thumbnail is too small to read it.
    expect(url).toContain("&attribution=0");
    // And the frame travels in the drawing rather than as a reference, since
    // the rasteriser resolves nothing external.
    expect(svg).toContain('href="data:image/png;base64,');
    expect(svg).not.toMatch(/href="https?:/);
  });

  it("keeps the placeholder map where the frame cannot be fetched", async () => {
    for (const outcome of ["status", "network"] as const) {
      clearStaticMapCache();
      stubFetch(outcome);

      const svg = await svgForLayout(withContent);

      expect(svg).not.toContain("<image");
      // The map glyph the drawing carries under the frame is what shows.
      const map = /<g data-type="map"[^>]*>([\s\S]*?)<\/g>/.exec(svg);
      expect(map?.[1]).toContain("<path ");
    }
  });

  it("gives up on a frame that does not answer in time", async () => {
    vi.useFakeTimers();
    stubFetch("hang");

    const pending = svgForLayout(withContent);
    await vi.advanceTimersByTimeAsync(STATIC_MAP_TIMEOUT);

    expect(await pending).not.toContain("<image");
  });

  it("asks for one frame per camera, however often the layout is drawn", async () => {
    const fetchMock = stubFetch("png");

    await svgForLayout(withContent);
    await svgForLayout(withContent);

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("writes a text block's own words, in the markup the author wrote", async () => {
    stubFetch("png");

    const svg = await svgForLayout(withContent);

    const prose = /<foreignObject[\s\S]*?<\/foreignObject>/.exec(svg)?.[0] ?? "";
    expect(prose).toContain("Ridership 2026");
    expect(prose).toContain("<strong>");
    expect(prose).toContain("text-align: center");
    // In the ink the layout canvas writes it in, at the size its own run
    // asks for, scaled into the frame.
    expect(prose).toContain(`color: ${LAYOUT_SNAPSHOT_PALETTE.text}`);
    expect(prose).toMatch(/font-size: [\d.]+px/);
    // The placeholder text lines are gone: the block carries real words now.
    const text = /<g data-type="text"[\s\S]*?<\/g>/.exec(svg)?.[0] ?? "";
    expect(positionedRects(text)).toHaveLength(0);
  });

  it("writes a legend's own title above its rows", async () => {
    stubFetch("png");

    const svg = await svgForLayout(withContent);

    expect(svg).toContain(">Stops per hour</text>");
    expect(svg).toContain(`fill="${LAYOUT_SNAPSHOT_PALETTE.text}"`);
    // The swatch rows are still drawn, below the title.
    const legend = /<g data-type="legend"[^>]*>([\s\S]*?)<\/g>/.exec(svg)?.[1] ?? "";
    const [title] = [...legend.matchAll(/<text[^>]*y="([\d.]+)"/g)].map((match) => Number(match[1]));
    const rows = positionedRects(legend).map(([, y]) => y);
    expect(rows.length).toBeGreaterThan(1);
    expect(Math.max(...rows)).toBeGreaterThan(title);
  });

  it("escapes a legend title's own characters into the document", async () => {
    stubFetch("png");

    const svg = await svgForLayout({
      ...withContent,
      elements: [{ type: "legend", x: 10, y: 10, width: 90, height: 60, title: 'A & B <"x">' }],
    });

    expect(svg).toContain("A &amp; B &lt;&quot;x&quot;&gt;");
    expect(svg).not.toContain('<"x">');
  });

  it("frames and fills a block only where the block itself asks for it", async () => {
    stubFetch("png");

    const svg = await svgForLayout({
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
    });

    const groups = [...svg.matchAll(/<g data-type="table"[^>]*>[\s\S]*?<\/g>/g)].map((match) => match[0]);
    // The block that asks for nothing shows its content and no frame at all
    // — an outlining rect is what a frame is written as.
    expect(groups[0]).not.toContain('fill="none"');
    expect(groups[0]).not.toContain("fill-opacity");
    expect(groups[0]).toContain(`fill="${LAYOUT_SNAPSHOT_PALETTE.glyph.tint}"`);
    // The one that asks gets its own colours, its width scaled from the
    // millimetre it names, and its own opacity on the block as a whole.
    expect(groups[1]).toContain('stroke="#1A73E8"');
    expect(groups[1]).toContain('fill="#FFF3CD" fill-opacity="0.4"');
    expect(groups[1]).toMatch(/stroke-width="[\d.]+"/);
    const width = Number(/stroke-width="([\d.]+)"/.exec(groups[1])?.[1]);
    expect(width).toBeGreaterThan(1);
    expect(groups[1]).toContain('opacity="0.8"');
  });

  it("draws the faintest outline for a block with nothing at all to show", async () => {
    const svg = await svgForLayout({
      kind: "layout",
      orientation: "portrait",
      page: { width: 210, height: 297 },
      elements: [{ type: "something_new", x: 10, y: 10, width: 100, height: 40 }],
    });

    expect(svg).toContain(`stroke="${LAYOUT_SNAPSHOT_PALETTE.elementStroke}"`);
  });

  it("keeps a block's content inside the padding it asks for", async () => {
    const fetchMock = stubFetch("png");

    await svgForLayout({
      kind: "layout",
      orientation: "landscape",
      page: { width: 297, height: 210 },
      elements: [
        {
          type: "map",
          x: 10,
          y: 10,
          width: 200,
          height: 150,
          viewState: { latitude: 48.1374, longitude: 11.5755, zoom: 11.5 },
          style: { padding: 10 },
        },
      ],
    });

    // The frame asked for is the padded box, not the element's own.
    const [padded] = fetchMock.mock.calls[0] as [string];
    const [wide] = /(\d+)x(\d+)@2x/.exec(padded)?.slice(1).map(Number) ?? [0];
    clearStaticMapCache();
    await svgForLayout(withContent);
    const [full] = fetchMock.mock.calls[1] as [string];
    const [fullWide] = /(\d+)x(\d+)@2x/.exec(full)?.slice(1).map(Number) ?? [0];
    expect(wide).toBeLessThan(fullWide);
  });

  it("takes the size it is given, and scales the wireframe's own hairlines with it", async () => {
    const small = await svgForLayout(descriptor, SCAFFOLD_FRAME);

    expect(small).toContain(`viewBox="0 0 ${SCAFFOLD_FRAME.width} ${SCAFFOLD_FRAME.height}"`);
    // At the scaffold's own frame the page's border is the 1px hairline the
    // scaffold draws; at the snapshot's size it is drawn proportionally
    // thicker, so the picture reads the same.
    expect(layoutDrawing(descriptor, { size: SCAFFOLD_FRAME }).page.border).toBe(1);
    expect(layoutDrawing(descriptor, { size: SNAPSHOT_SIZE }).page.border).toBeGreaterThan(1);
  });
});

describe("renderLayoutSnapshot", () => {
  it("resolves the PNG the canvas produced", async () => {
    stubImage("load");
    const blob = new Blob(["png"], { type: "image/png" });
    const context = stubCanvas(blob);

    await expect(renderLayoutSnapshot(descriptor)).resolves.toBe(blob);
    expect(context.drawImage).toHaveBeenCalledTimes(1);
    // The ground is painted under the drawing, so a transparent corner of
    // the PNG is the ground rather than black.
    expect(context.fillRect).toHaveBeenCalledWith(0, 0, SNAPSHOT_SIZE.width, SNAPSHOT_SIZE.height);
  });

  it("rejects when the image cannot be loaded", async () => {
    stubImage("error");
    stubCanvas(new Blob(["png"], { type: "image/png" }));

    await expect(renderLayoutSnapshot(descriptor)).rejects.toThrow(/image failed to load/i);
  });

  it("rejects when the canvas hands back no blob", async () => {
    stubImage("load");
    stubCanvas(null);

    await expect(renderLayoutSnapshot(descriptor)).rejects.toThrow(/no PNG/i);
  });

  it("rejects when there is no 2D context to draw into", async () => {
    stubImage("load");
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);

    await expect(renderLayoutSnapshot(descriptor)).rejects.toThrow(/context/i);
  });
});
