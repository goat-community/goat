import { configureStore } from "@reduxjs/toolkit";
import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { Provider } from "react-redux";
import { describe, expect, it, vi } from "vitest";

import { mapReducer } from "@/lib/store/map/slice";

import { useBasemap } from "@/hooks/map/MapHooks";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { exists: () => false } }),
}));

const customId = "00000000-0000-0000-0000-000000000001";
const projectA = { id: "project-a", basemap: "dark", custom_basemaps: [] };
const projectB = {
  id: "project-b",
  basemap: customId,
  custom_basemaps: [
    {
      type: "vector" as const,
      id: customId,
      name: "Custom Vector",
      url: "https://example.com/style.json",
      created_at: "2026-04-30T00:00:00Z",
      updated_at: "2026-04-30T00:00:00Z",
    },
  ],
};

const makeWrapper = () => {
  const store = configureStore({ reducer: { map: mapReducer } });
  const wrapper = ({ children }: { children: ReactNode }) => <Provider store={store}>{children}</Provider>;
  return wrapper;
};

describe("useBasemap with a basemap stored for another project", () => {
  it("starts the next project on its own basemap, not the previous one's", () => {
    const wrapper = makeWrapper();
    const a = renderHook(() => useBasemap(projectA), { wrapper });
    act(() => a.result.current.setActiveBasemap("dark"));
    expect(a.result.current.activeBasemap.value).toBe("dark");

    const b = renderHook(() => useBasemap(projectB), { wrapper });
    expect(b.result.current.activeBasemap.value).toBe(customId);
    expect(b.result.current.mapStyle).toBe("https://example.com/style.json");
  });

  it("keeps a basemap picked for the same project", () => {
    const wrapper = makeWrapper();
    const b = renderHook(() => useBasemap(projectB), { wrapper });
    act(() => b.result.current.setActiveBasemap("dark"));
    expect(b.result.current.activeBasemap.value).toBe("dark");
  });
});
