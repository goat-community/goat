import type { Job } from "@/lib/api/processes";

type Translate = (key: string, vars?: Record<string, unknown>) => string;

/**
 * What the job tray and the job toasts call a job: its tool's label, or for
 * a template copy the entry it is copied for ("Copy: Vorhaben (Eingabe)"),
 * which core hands the job as `layer_name` — several copies started by one
 * template would otherwise all read "Copy dataset".
 */
export const jobLabel = (job: Pick<Job, "processID" | "inputs">, t: Translate): string => {
  const name = job.inputs?.["layer_name"];
  if (job.processID === "layer_copy" && typeof name === "string" && name.trim()) {
    return t("layer_copy_named", { name });
  }
  return t(job.processID) || job.processID;
};
