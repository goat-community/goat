import { describe, expect, it } from "vitest";

import { isApplePlatform, shortcutLabel } from "@/lib/utils/platform";

describe("isApplePlatform", () => {
  it("trusts the user-agent platform hint when the browser exposes one", () => {
    expect(isApplePlatform({ userAgentData: { platform: "macOS" } })).toBe(true);
    expect(isApplePlatform({ userAgentData: { platform: "Windows" } })).toBe(false);
    expect(isApplePlatform({ userAgentData: { platform: "Linux" } })).toBe(false);
  });

  it("does not fall back to the legacy fields once the hint says not Apple", () => {
    expect(isApplePlatform({ userAgentData: { platform: "Windows" }, platform: "MacIntel" })).toBe(false);
  });

  it("falls back to navigator.platform in browsers with no hint", () => {
    expect(isApplePlatform({ platform: "MacIntel" })).toBe(true);
    expect(isApplePlatform({ platform: "Win32" })).toBe(false);
    expect(isApplePlatform({ platform: "Linux x86_64" })).toBe(false);
  });

  it("reads an iPad, which reports a Mac platform, as Apple", () => {
    expect(isApplePlatform({ platform: "MacIntel", maxTouchPoints: 5 })).toBe(true);
    expect(isApplePlatform({ platform: "iPhone" })).toBe(true);
  });

  it("falls back to the user agent when platform is empty", () => {
    expect(
      isApplePlatform({ platform: "", userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" })
    ).toBe(true);
    expect(isApplePlatform({ platform: "", userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" })).toBe(
      false
    );
  });

  it("assumes not Apple when the browser tells us nothing", () => {
    expect(isApplePlatform({})).toBe(false);
  });
});

describe("shortcutLabel", () => {
  it("uses the Command symbol on Apple hardware, with no separator", () => {
    expect(shortcutLabel("K", { userAgentData: { platform: "macOS" } })).toBe("⌘K");
  });

  it("spells the modifier out everywhere else, since no other keyboard has that key", () => {
    expect(shortcutLabel("K", { userAgentData: { platform: "Windows" } })).toBe("Ctrl+K");
    expect(shortcutLabel("K", { platform: "Linux x86_64" })).toBe("Ctrl+K");
  });

  it("names the Ctrl key as the caller's keyboard labels it", () => {
    expect(shortcutLabel("K", { platform: "Win32" }, "Strg")).toBe("Strg+K");
    expect(shortcutLabel("K", { platform: "MacIntel" }, "Strg")).toBe("⌘K");
  });
});
