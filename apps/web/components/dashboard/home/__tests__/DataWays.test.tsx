import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import DataWays from "@/components/dashboard/home/DataWays";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

describe("DataWays", () => {
  it("calls onCatalog when the catalog card's action is clicked", () => {
    const onCatalog = vi.fn();
    render(<DataWays onUpload={vi.fn()} onCatalog={onCatalog} />);

    fireEvent.click(screen.getByRole("button", { name: "browse_catalog" }));

    expect(onCatalog).toHaveBeenCalled();
  });

  it("calls onUpload when the upload card's action is clicked", () => {
    const onUpload = vi.fn();
    render(<DataWays onUpload={onUpload} onCatalog={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "upload_dataset" }));

    expect(onUpload).toHaveBeenCalled();
  });

  it("renders the section header and both card titles", () => {
    render(<DataWays onUpload={vi.fn()} onCatalog={vi.fn()} />);

    expect(screen.getByText("get_some_data_in")).toBeInTheDocument();
    expect(screen.getByText("data_way_catalog_title")).toBeInTheDocument();
    expect(screen.getByText("data_way_upload_title")).toBeInTheDocument();
  });
});
