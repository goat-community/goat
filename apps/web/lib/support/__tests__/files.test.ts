import { describe, expect, it } from "vitest";

import { SUPPORT_MAX_FILE_BYTES, SUPPORT_MAX_TOTAL_BYTES, checkFiles } from "@/lib/support/files";

const file = (name: string, bytes: number) => new File([new Uint8Array(bytes)], name);

describe("checkFiles", () => {
  it("accepts up to 10 files within the limits", () => {
    expect(checkFiles(Array.from({ length: 10 }, (_, i) => file(`f${i}`, 10)))).toEqual({ ok: true });
  });
  it("rejects an 11th file", () => {
    expect(checkFiles(Array.from({ length: 11 }, (_, i) => file(`f${i}`, 10)))).toEqual({
      ok: false,
      reason: "too_many_files",
    });
  });
  it("rejects a file over 10 MB and names it", () => {
    expect(checkFiles([file("big.bin", SUPPORT_MAX_FILE_BYTES + 1)])).toEqual({
      ok: false,
      reason: "file_too_large",
      name: "big.bin",
    });
  });
  it("accepts a file of exactly 10 MB (core only rejects larger)", () => {
    expect(checkFiles([file("edge.bin", SUPPORT_MAX_FILE_BYTES)])).toEqual({ ok: true });
  });
  it("rejects more than 50 MB in total", () => {
    const nine = 9 * 1024 * 1024;
    expect(checkFiles(Array.from({ length: 6 }, (_, i) => file(`f${i}`, nine)))).toEqual({
      ok: false,
      reason: "files_too_large",
    });
  });
  it("accepts exactly 50 MB in total (core only rejects more)", () => {
    const each = SUPPORT_MAX_TOTAL_BYTES / 5;
    expect(checkFiles(Array.from({ length: 5 }, (_, i) => file(`f${i}`, each)))).toEqual({ ok: true });
  });
});
