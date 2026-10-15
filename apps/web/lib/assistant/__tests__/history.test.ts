import { describe, expect, it } from "vitest";

import { conversationTitle, groupByDay, originLabel } from "@/lib/assistant/history";
import type { ConversationSummary } from "@/lib/assistant/types";

const t = (key: string) => key;
const row = (patch: Partial<ConversationSummary>): ConversationSummary => ({
  id: "c1",
  title: null,
  origin_surface: "catalog",
  project_id: null,
  project_name: null,
  project_access: null,
  first_message: null,
  running: false,
  created_at: "2026-10-01T08:00:00Z",
  updated_at: "2026-10-01T08:00:00Z",
  ...patch,
});

describe("history labels", () => {
  it("titles a conversation by its title, else its first message", () => {
    expect(conversationTitle(row({ title: "Radwege", first_message: "x" }), t)).toBe("Radwege");
    expect(conversationTitle(row({ first_message: "Wo gibt es Radwege?" }), t)).toBe("Wo gibt es Radwege?");
    expect(conversationTitle(row({}), t)).toBe("assistant_untitled");
    expect(conversationTitle(undefined, t)).toBe("assistant_untitled");
  });

  it("labels the origin with the project and mode, the page, or a lost project", () => {
    expect(
      originLabel(
        row({
          project_id: "p1",
          project_name: "Berlin cycling study",
          project_access: true,
          origin_surface: "project.map",
        }),
        t
      )
    ).toBe("Berlin cycling study · map");
    expect(
      originLabel(
        row({ project_id: "p1", project_name: "B", project_access: true, origin_surface: "catalog" }),
        t
      )
    ).toBe("B");
    expect(
      originLabel(row({ project_id: "p1", project_access: false, origin_surface: "project.map" }), t)
    ).toBe("assistant_origin_project_unavailable");
    expect(originLabel(row({ origin_surface: "catalog" }), t)).toBe("catalog");
    expect(originLabel(row({ origin_surface: "home" }), t)).toBe("home");
    expect(originLabel(row({ origin_surface: "spike" }), t)).toBe("assistant_origin_other");
  });

  it("groups by today and earlier", () => {
    const now = new Date("2026-10-01T12:00:00Z");
    const groups = groupByDay(
      [
        row({ id: "a", updated_at: "2026-10-01T09:00:00Z" }),
        row({ id: "b", updated_at: "2026-09-29T09:00:00Z" }),
      ],
      now
    );
    expect(groups.today.map((c) => c.id)).toEqual(["a"]);
    expect(groups.earlier.map((c) => c.id)).toEqual(["b"]);
  });
});
