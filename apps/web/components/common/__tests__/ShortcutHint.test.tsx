import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ShortcutHint from "@/components/common/ShortcutHint";

const setPlatform = (value: string) =>
  Object.defineProperty(window.navigator, "platform", { value, configurable: true });

describe("ShortcutHint", () => {
  const original = window.navigator.platform;
  beforeEach(() => vi.restoreAllMocks());
  afterEach(() => setPlatform(original));

  it("shows the Command symbol on a Mac", () => {
    setPlatform("MacIntel");
    render(<ShortcutHint letter="K" />);
    expect(screen.getByText("⌘K")).toBeInTheDocument();
  });

  it("shows Ctrl on Windows, where there is no Command key to press", () => {
    setPlatform("Win32");
    render(<ShortcutHint letter="K" />);
    expect(screen.getByText("Ctrl+K")).toBeInTheDocument();
    expect(screen.queryByText("⌘K")).not.toBeInTheDocument();
  });

  it("shows Ctrl on Linux", () => {
    setPlatform("Linux x86_64");
    render(<ShortcutHint letter="K" />);
    expect(screen.getByText("Ctrl+K")).toBeInTheDocument();
  });

  it("renders a kbd element, so assistive tech announces it as a key", () => {
    setPlatform("Win32");
    const { container } = render(<ShortcutHint letter="K" />);
    expect(container.querySelector("kbd")).not.toBeNull();
  });

  describe("on a device without a mouse or trackpad", () => {
    const original = window.matchMedia;
    const setFinePointer = (fine: boolean) => {
      window.matchMedia = ((query: string) =>
        ({
          matches: query.includes("pointer: fine") ? fine : false,
          media: query,
        }) as MediaQueryList) as typeof window.matchMedia;
    };
    afterEach(() => {
      window.matchMedia = original;
    });

    it("shows nothing on a phone or tablet, which has no keyboard to press it on", () => {
      setPlatform("iPhone");
      setFinePointer(false);
      const { container } = render(<ShortcutHint letter="K" />);
      expect(container.querySelector("kbd")).toBeNull();
    });

    it("shows the hint where a mouse or trackpad is attached", () => {
      setPlatform("Win32");
      setFinePointer(true);
      render(<ShortcutHint letter="K" />);
      expect(screen.getByText("Ctrl+K")).toBeInTheDocument();
    });
  });
});
