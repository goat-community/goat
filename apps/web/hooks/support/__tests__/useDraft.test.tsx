import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useDraft } from "@/hooks/support/useDraft";

describe("useDraft", () => {
  beforeEach(() => localStorage.clear());

  it("restores, updates and clears a draft", () => {
    localStorage.setItem("goat:support:draft:reply:00031", JSON.stringify("half a reply"));
    const { result } = renderHook(() => useDraft("reply:00031", ""));
    expect(result.current[0]).toBe("half a reply");
    act(() => result.current[1]("full reply"));
    expect(JSON.parse(localStorage.getItem("goat:support:draft:reply:00031")!)).toBe("full reply");
    act(() => result.current[2]());
    expect(localStorage.getItem("goat:support:draft:reply:00031")).toBeNull();
    expect(result.current[0]).toBe("");
  });

  it("works without a key (no storage)", () => {
    const { result } = renderHook(() => useDraft<string>(null, "x"));
    act(() => result.current[1]("y"));
    expect(result.current[0]).toBe("y");
    expect(localStorage.length).toBe(0);
  });

  it("switches to the stored draft of the new key when the key changes", () => {
    localStorage.setItem("goat:support:draft:reply:00031", JSON.stringify("draft 31"));
    localStorage.setItem("goat:support:draft:reply:00032", JSON.stringify("draft 32"));
    const { result, rerender } = renderHook(({ k }) => useDraft(k, ""), {
      initialProps: { k: "reply:00031" },
    });
    expect(result.current[0]).toBe("draft 31");
    rerender({ k: "reply:00032" });
    expect(result.current[0]).toBe("draft 32");
    act(() => result.current[1]("edited 32"));
    expect(JSON.parse(localStorage.getItem("goat:support:draft:reply:00032")!)).toBe("edited 32");
    expect(JSON.parse(localStorage.getItem("goat:support:draft:reply:00031")!)).toBe("draft 31");
    rerender({ k: "reply:00099" });
    expect(result.current[0]).toBe("");
  });

  it("keeps clear stable when `initial` is a new object each render", () => {
    const { result, rerender } = renderHook(() => useDraft("form:1", { a: "" }));
    const first = result.current[2];
    rerender();
    expect(result.current[2]).toBe(first);
    act(() => result.current[1]({ a: "x" }));
    act(() => result.current[2]());
    expect(result.current[0]).toEqual({ a: "" });
  });
});
