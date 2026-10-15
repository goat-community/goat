import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { MatomoTracker } from "@/components/analytics/MatomoTracker";

// next/script injects nothing in jsdom; render its body inline so the
// generated tracker code can be read back.
vi.mock("next/script", () => ({
  default: ({ id, children }: { id: string; children: ReactNode }) => (
    <script data-testid={id}>{children}</script>
  ),
}));

const renderTracker = (requireConsent?: boolean) =>
  render(
    <MatomoTracker
      url="https://example.matomo.cloud/"
      siteId="5"
      projectId="p1"
      projectName="Stadtklimadashboard"
      requireConsent={requireConsent}
    />
  ).getByTestId("matomo-tracker").textContent ?? "";

describe("MatomoTracker", () => {
  it("waits for consent by default, so the banner decides whether anything is sent", () => {
    const code = renderTracker();
    expect(code).toContain("_paq.push(['requireConsent']);");
    expect(code).not.toContain("disableCookies");
  });

  it("runs cookieless when there is no banner, so nothing is stored on the device", () => {
    const code = renderTracker(false);
    expect(code).toContain("_paq.push(['disableCookies']);");
    expect(code).not.toContain("requireConsent");
  });

  it("switches cookies off before the first pageview, which would otherwise set _pk_id", () => {
    const code = renderTracker(false);
    expect(code.indexOf("disableCookies")).toBeLessThan(code.indexOf("trackPageView"));
  });
});
