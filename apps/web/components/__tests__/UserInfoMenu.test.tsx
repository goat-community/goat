import { fireEvent, render } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import UserInfoMenu from "@/components/UserInfoMenu";

const { countsMock } = vi.hoisted(() => ({ countsMock: vi.fn() }));
vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("next-auth/react", () => ({ signOut: vi.fn() }));
vi.mock("@/lib/api/users", () => ({
  useOrganization: () => ({ organization: { name: "Org" } }),
  useUserProfile: () => ({ userProfile: { firstname: "A", lastname: "B", roles: [] } }),
}));
vi.mock("@/components/support/SupportMenu", () => ({
  SupportMenuEntries: () => null,
  supportCountLabel: (_t: unknown, c: { needsReply: number; unread: number }) =>
    c.needsReply ? `to_answer:${c.needsReply}` : c.unread ? `unread:${c.unread}` : undefined,
  useSupportCounts: countsMock,
}));

const dot = (container: HTMLElement) => container.querySelector(".MuiBadge-dot");

describe("UserInfoMenu support dot", () => {
  beforeEach(() => countsMock.mockReset());

  it("is warning-coloured when tickets wait for an answer", () => {
    countsMock.mockReturnValue({ needsReply: 1, unread: 2 });
    const { container } = render(<UserInfoMenu withSupport />);
    expect(dot(container)?.classList.contains("MuiBadge-invisible")).toBe(false);
    expect(dot(container)?.classList.contains("MuiBadge-colorWarning")).toBe(true);
  });

  it("is primary-coloured when tickets are only unread", () => {
    countsMock.mockReturnValue({ needsReply: 0, unread: 2 });
    const { container } = render(<UserInfoMenu withSupport />);
    expect(dot(container)?.classList.contains("MuiBadge-invisible")).toBe(false);
    expect(dot(container)?.classList.contains("MuiBadge-colorPrimary")).toBe(true);
    expect(container.querySelector("button")?.getAttribute("aria-label")).toBe("account_menu: unread:2");
  });

  it("is named as the account menu, says whether it is open, and adds the count", () => {
    countsMock.mockReturnValue(null);
    const { container } = render(<UserInfoMenu />);
    const button = container.querySelector("button");
    expect(button?.getAttribute("aria-label")).toBe("account_menu");
    expect(button?.getAttribute("aria-expanded")).toBe("false");
    fireEvent.click(button as HTMLButtonElement);
    expect(button?.getAttribute("aria-expanded")).toBe("true");
  });

  it("is hidden when nothing is waiting or support is off", () => {
    countsMock.mockReturnValue({ needsReply: 0, unread: 0 });
    const { container, rerender } = render(<UserInfoMenu withSupport />);
    expect(dot(container)?.classList.contains("MuiBadge-invisible")).toBe(true);
    countsMock.mockReturnValue(null);
    rerender(<UserInfoMenu withSupport />);
    expect(dot(container)?.classList.contains("MuiBadge-invisible")).toBe(true);
  });
});
