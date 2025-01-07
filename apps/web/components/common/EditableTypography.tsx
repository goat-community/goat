import type { InputProps } from "@mui/material";
import { Input } from "@mui/material";
import type { TypographyProps } from "@mui/material/Typography";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import * as React from "react";

export interface EditableTypographyProps {
  onChange?: (value: string) => void;
  onBlur?: (value: string) => void;
  value?: string;
  readOnly?: boolean;
  isEditing?: boolean;
}

const InputWithChildren = ({ children, ...props }: InputProps & { children?: React.ReactNode }) => {
  let value = "";
  if (children) {
    if (typeof children == "string" || typeof children == "number") {
      value = children.toString();
    }
  }

  return (
    <Input
      {...props}
      value={value}
      readOnly={props.readOnly}
      disableUnderline={props.readOnly}
      sx={{
        "& .MuiInputBase-input": {
          overflow: "hidden",
          textOverflow: "ellipsis",
        },
      }}
      inputProps={{ className: props.className }}
    />
  );
};

/**
 * Displaying like a `Typography`. But acting as an `input`
 */
const EditableTypography = ({
  onChange: propsOnChange,
  onBlur: propsOnBlur,
  value: propsValue,
  readOnly = false,
  isEditing: _isEditing = false,
  ...props
}: EditableTypographyProps & TypographyProps) => {
  const [internalValue, setInternalValue] = useState(propsValue || "");
  const [isEditing, setIsEditing] = useState(_isEditing);

  React.useEffect(() => {
    setIsEditing(_isEditing);
  }, [_isEditing]);

  const onChange = (value: string) => {
    if (propsOnChange) {
      propsOnChange(value);
    }
    setInternalValue(value);
  };

  const onBlur = () => {
    setIsEditing(false);
    if (propsOnBlur) {
      propsOnBlur(internalValue);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <Typography
      {...props}
      onDoubleClick={() => {
        if (!readOnly) {
          setIsEditing(true);
        }
      }}
      key={isEditing ? "input" : "typography"}
      component={InputWithChildren}
      onBlur={onBlur}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          onBlur();
        }
      }}
      sx={{
        cursor: "auto",
      }}
      readOnly={!isEditing}
      autoFocus={isEditing}
      onChange={handleChange}>
      {internalValue}
    </Typography>
  );
};

export default EditableTypography;
