import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import {
  HeaderPopoverExternalMark,
  HeaderPopoverFooter,
  HeaderPopoverFooterAction,
  HeaderPopoverHeader,
  HeaderPopoverList,
  HeaderPopoverRow,
} from "@/components/header/HeaderPopover";

describe("HeaderPopoverHeader", () => {
  it("shows the title, the aside and what is placed below", () => {
    render(
      <HeaderPopoverHeader title="Getting started" aside="1/6 completed" leading={<i data-testid="lead" />}>
        <div data-testid="below" />
      </HeaderPopoverHeader>
    );
    expect(screen.getByText("Getting started")).toBeTruthy();
    expect(screen.getByText("1/6 completed")).toBeTruthy();
    expect(screen.getByTestId("lead")).toBeTruthy();
    expect(screen.getByTestId("below")).toBeTruthy();
  });

  it("has no aside unless given one", () => {
    const { container } = render(<HeaderPopoverHeader title="Support" />);
    expect(container.querySelectorAll("p")).toHaveLength(1);
  });
});

describe("HeaderPopoverList", () => {
  it("wraps its rows", () => {
    render(
      <HeaderPopoverList>
        <span>row</span>
      </HeaderPopoverList>
    );
    expect(screen.getByText("row")).toBeTruthy();
  });
});

describe("HeaderPopoverRow", () => {
  it("is a button that clicks, with a secondary line and trailing content", () => {
    const onClick = vi.fn();
    render(
      <HeaderPopoverRow
        icon={ICON_NAME.HELP}
        label="Tickets"
        secondary="#1 · Anna"
        trailing={<b>2</b>}
        onClick={onClick}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /Tickets/ }));
    expect(onClick).toHaveBeenCalled();
    expect(screen.getByText("#1 · Anna")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
  });

  it("is a link with href, in a new tab when asked, a plain element without either", () => {
    const { rerender } = render(<HeaderPopoverRow label="Docs" href="https://x.test" newTab />);
    const link = screen.getByRole("link", { name: "Docs" });
    expect(link.getAttribute("href")).toBe("https://x.test");
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toBe("noopener noreferrer");
    rerender(<HeaderPopoverRow label="Mail" href="mailto:a@b.c" />);
    expect(screen.getByRole("link", { name: "Mail" }).getAttribute("target")).toBeNull();
    rerender(<HeaderPopoverRow label="Done" />);
    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.queryByRole("link")).toBeNull();
  });

  it("does nothing while disabled", () => {
    const onClick = vi.fn();
    render(<HeaderPopoverRow label="Off" onClick={onClick} disabled />);
    fireEvent.click(screen.getByRole("button", { name: "Off" }));
    expect(onClick).not.toHaveBeenCalled();
  });

  it("takes your own node as the icon, and a danger tone", () => {
    render(
      <HeaderPopoverRow label="Log out" tone="danger" icon={<i data-testid="dot" />} onClick={vi.fn()} />
    );
    expect(screen.getByTestId("dot")).toBeTruthy();
  });
});

describe("HeaderPopoverFooter", () => {
  it("holds a button action and a link action", () => {
    const onClick = vi.fn();
    render(
      <HeaderPopoverFooter>
        <HeaderPopoverFooterAction onClick={onClick}>Skip</HeaderPopoverFooterAction>
        <HeaderPopoverFooterAction href="https://x.test" newTab>
          All <HeaderPopoverExternalMark />
        </HeaderPopoverFooterAction>
      </HeaderPopoverFooter>
    );
    fireEvent.click(screen.getByRole("button", { name: "Skip" }));
    expect(onClick).toHaveBeenCalled();
    expect(screen.getByRole("link", { name: /All/ }).getAttribute("target")).toBe("_blank");
  });
});
