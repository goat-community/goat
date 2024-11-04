import AttachFileIcon from "@mui/icons-material/AttachFile";
import CloseIcon from "@mui/icons-material/Close";
import type { InputBaseComponentProps } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import type { TextFieldProps as MuiTextFieldProps } from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material/styles";
import prettyBytes from "pretty-bytes";
import React from "react";

import { fileListToArray, getFileDetails, getTotalFilesSize, matchIsFile } from "@/lib/utils/file";

type NonUndefined<T> = T extends undefined ? never : T;

type TextFieldProps = Omit<MuiTextFieldProps, "onChange" | "select" | "type" | "multiline" | "defaultValue">;

export type MuiFileInputProps<T extends boolean | undefined> = TextFieldProps & {
  value?: T extends true ? File[] : File | null;
  hideSizeText?: boolean;
  multiple?: T;
  getInputText?: (files: T extends true ? File[] : File | null) => string;
  getSizeText?: (files: T extends true ? File[] : File | null) => string;
  onChange?: (value: T extends true ? File[] : File | null) => void;
};

type InputProps = InputBaseComponentProps & {
  text: string | { filename: string; extension: string };
  isPlaceholder: boolean;
};

const Label = styled("label")`
  position: relative;
  flex-grow: 1;

  input {
    opacity: 0 !important;
  }

  & > span {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 2;
    display: flex;
    align-items: center;
  }

  span.MuiFileInput-placeholder {
    color: gray;
  }
`;

const Filename = styled("div")`
  display: flex;
  width: 100%;

  & > span {
    display: block;
  }

  & > span:first-of-type {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }

  & > span:last-of-type {
    flex-shrink: 0;
    display: block;
  }
`;

// eslint-disable-next-line react/display-name
const Input = React.forwardRef((props: InputProps, ref: React.ForwardedRef<HTMLInputElement>) => {
  const { text, isPlaceholder, placeholder, ...restInputProps } = props;
  // eslint-disable-next-line react/hook-use-state
  const id = React.useId();

  return (
    <Label htmlFor={id}>
      <input {...restInputProps} ref={ref} id={id} />
      {text ? (
        <span aria-placeholder={placeholder} className={isPlaceholder ? "MuiFileInput-placeholder" : ""}>
          {typeof text === "string" ? (
            text
          ) : (
            <Filename>
              <span>{text.filename}</span>
              <span>.{text.extension}</span>
            </Filename>
          )}
        </span>
      ) : null}
    </Label>
  );
});

const MuiFileInput = <T extends boolean | undefined>(
  props: MuiFileInputProps<T>,
  propRef: MuiFileInputProps<T>["ref"]
) => {
  const {
    value,
    onChange,
    disabled,
    getInputText,
    getSizeText,
    placeholder,
    hideSizeText,
    inputProps,
    InputProps,
    multiple,
    className,
    ...restTextFieldProps
  } = props;
  const inputRef = React.useRef<HTMLInputElement>(null);
  const isMultiple =
    multiple || (inputProps?.multiple as boolean) || (InputProps?.inputProps?.multiple as boolean) || false;

  const clearInputValue = () => {
    const inputEl = inputRef.current;

    if (inputEl) {
      inputEl.value = "";
    }
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = event.target.files;
    const files = fileList ? fileListToArray(fileList) : [];
    clearInputValue();

    if (isMultiple) {
      onChange?.(files as NonNullable<typeof value>);
    } else {
      onChange?.(files[0] as unknown as NonNullable<typeof value>);
    }
  };

  const handleClearAll = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();

    if (disabled) {
      return;
    }

    if (multiple) {
      onChange?.([] as unknown as NonNullable<typeof value>);
    } else {
      onChange?.(null as NonUndefined<typeof value>);
    }
  };

  const hasAtLeastOneFile = Array.isArray(value) ? value.length > 0 : matchIsFile(value);

  const getTheInputText = () => {
    if (value === null || (Array.isArray(value) && value.length === 0)) {
      return placeholder || "";
    }

    if (typeof getInputText === "function" && value !== undefined) {
      return getInputText(value);
    }

    if (value && hasAtLeastOneFile) {
      if (Array.isArray(value) && value.length > 1) {
        return `${value.length} files`;
      }

      return getFileDetails(value);
    }

    return "";
  };

  const getTotalSizeText = (): string => {
    if (typeof getSizeText === "function" && value !== undefined) {
      return getSizeText(value);
    }

    if (hasAtLeastOneFile) {
      if (Array.isArray(value)) {
        const totalSize = getTotalFilesSize(value);

        return prettyBytes(totalSize);
      }

      if (matchIsFile(value)) {
        return prettyBytes(value.size);
      }
    }

    return "";
  };

  return (
    <TextField
      ref={propRef}
      type="file"
      disabled={disabled}
      onChange={handleChange}
      className={`MuiFileInput-TextField ${className || ""}`}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <AttachFileIcon />
          </InputAdornment>
        ),
        endAdornment: (
          <InputAdornment position="end" style={{ visibility: hasAtLeastOneFile ? "visible" : "hidden" }}>
            {!hideSizeText ? (
              <Typography variant="caption" mr="2px" className="MuiFileInput-Typography-size-text">
                {getTotalSizeText()}
              </Typography>
            ) : null}
            <IconButton
              aria-label="Clear"
              size="small"
              disabled={disabled}
              className="MuiFileInput-IconButton"
              onClick={handleClearAll}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </InputAdornment>
        ),
        ...InputProps,
        inputProps: {
          text: getTheInputText(),
          multiple: isMultiple,
          isPlaceholder: value === null || (Array.isArray(value) && value.length === 0),
          ref: inputRef,
          placeholder,
          ...inputProps,
          ...InputProps?.inputProps,
        },
        inputComponent: Input,
      }}
      {...restTextFieldProps}
    />
  );
};

const MuiFileInputForwarded = React.forwardRef(MuiFileInput) as <T extends boolean | undefined = false>(
  props: MuiFileInputProps<T> & { ref?: MuiFileInputProps<T>["ref"] }
) => ReturnType<typeof MuiFileInput<T>>;

export { MuiFileInputForwarded as MuiFileInput };
