import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import SetupChecklist from "@/components/dashboard/home/SetupChecklist";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) =>
      options ? `${key}(${Object.values(options).join(",")})` : key,
  }),
}));

describe("SetupChecklist", () => {
  it("shows the done count against the total", () => {
    render(<SetupChecklist done={["project"]} onStep={vi.fn()} />);

    expect(screen.getByText("n_of_m_done(1,6)")).toBeInTheDocument();
  });

  it("marks the first open step's action as the primary one", () => {
    render(<SetupChecklist done={["project"]} onStep={vi.fn()} />);

    // "project" is done, so "data" is the first open step.
    const dataCta = screen.getByRole("button", { name: "upload_dataset" });
    const catalogCta = screen.getByRole("button", { name: "browse_catalog" });
    expect(dataCta.className).toContain("MuiButton-contained");
    expect(catalogCta.className).toContain("MuiButton-outlined");
  });

  it("renders no action for a step already done", () => {
    render(<SetupChecklist done={["project"]} onStep={vi.fn()} />);

    expect(screen.queryByRole("button", { name: "new_project" })).not.toBeInTheDocument();
    expect(screen.getByText("step_project_title")).toBeInTheDocument();
  });

  it("calls onStep with the step id when its action is clicked", () => {
    const onStep = vi.fn();
    render(<SetupChecklist done={[]} onStep={onStep} />);

    fireEvent.click(screen.getByRole("button", { name: "new_project" }));

    expect(onStep).toHaveBeenCalledWith("project");
  });

  it("compact hides the 4th+ open steps behind Show all", () => {
    render(<SetupChecklist done={[]} compact onStep={vi.fn()} />);

    expect(screen.getByRole("button", { name: "new_project" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "upload_dataset" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "browse_catalog" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "pick_a_template" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "pick_a_workflow" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "invite_people" })).not.toBeInTheDocument();
    expect(screen.getByText("show_all_steps(6)")).toBeInTheDocument();
  });

  it("show all reveals the remaining steps", () => {
    render(<SetupChecklist done={[]} compact onStep={vi.fn()} />);

    fireEvent.click(screen.getByText("show_all_steps(6)"));

    expect(screen.getByRole("button", { name: "pick_a_template" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "pick_a_workflow" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "invite_people" })).toBeInTheDocument();
  });

  it("without compact, shows every open step", () => {
    render(<SetupChecklist done={[]} onStep={vi.fn()} />);

    expect(screen.getByRole("button", { name: "invite_people" })).toBeInTheDocument();
    expect(screen.queryByText("show_all_steps(6)")).not.toBeInTheDocument();
  });
});
