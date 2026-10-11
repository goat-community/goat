/**
 * One workflow variable's value field in the toolbox's workflow run view.
 *
 * The people filling these in rarely wrote the workflow, so the field is
 * titled with the variable's label (falling back to its name) and its
 * description is the field's help text. The technical name never shows here:
 * nothing is typed into an expression.
 */
import { Stack, TextField } from "@mui/material";

import {
  type WorkflowVariable,
  getVariableDescription,
  getVariableDisplayName,
} from "@/lib/validations/workflow";

import FormLabelHelper from "@/components/common/FormLabelHelper";

interface WorkflowRunVariableFieldProps {
  variable: WorkflowVariable;
  value: string | number | undefined;
  onChange: (value: string | number) => void;
  disabled?: boolean;
}

export default function WorkflowRunVariableField({
  variable,
  value,
  onChange,
  disabled,
}: WorkflowRunVariableFieldProps) {
  const label = getVariableDisplayName(variable);
  const description = getVariableDescription(variable);

  return (
    <Stack>
      <FormLabelHelper label={label} color="inherit" />
      <TextField
        size="small"
        type={variable.type === "number" ? "number" : "text"}
        value={value ?? ""}
        onChange={(e) => {
          const raw = e.target.value;
          onChange(variable.type === "number" ? (raw === "" ? "" : Number(raw)) : raw);
        }}
        inputProps={{ "aria-label": label }}
        helperText={description}
        disabled={disabled}
        fullWidth
      />
    </Stack>
  );
}
