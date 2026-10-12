import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import FilePicker from "@/components/support/FilePicker";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

describe("FilePicker", () => {
  it("adds the picked files and resets the input so the same file can be picked again", () => {
    const onChange = vi.fn();
    render(<FilePicker files={[]} onChange={onChange} />);
    const input = screen.getByTestId("support-file-input") as HTMLInputElement;
    const setValue = vi.fn();
    Object.defineProperty(input, "value", { configurable: true, get: () => "", set: setValue });
    const file = new File(["x"], "log.txt");
    fireEvent.change(input, { target: { files: [file] } });
    expect(setValue).toHaveBeenCalledWith("");
    expect(onChange).toHaveBeenCalledWith([file]);
  });

  it("shows a limit error and does not add files", () => {
    const onChange = vi.fn();
    render(<FilePicker files={[]} onChange={onChange} />);
    const big = new File(["x"], "big.bin");
    Object.defineProperty(big, "size", { value: 11 * 1024 * 1024 });
    fireEvent.change(screen.getByTestId("support-file-input"), { target: { files: [big] } });
    expect(onChange).not.toHaveBeenCalled();
    expect(screen.getByText("support_file_too_large")).toBeTruthy();
  });
});
