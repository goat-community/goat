// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable react-hooks/exhaustive-deps */

/* eslint-disable react/display-name */
import { MenuItem } from "@mui/material";
import InputAdornment from "@mui/material/InputAdornment";
import MuiTextField from "@mui/material/TextField";
import type { NonPostableEvtLike } from "evt";
import { useEvt } from "evt/hooks";
import { useConstCallback } from "powerhooks/useConstCallback";
import { useDomRect } from "powerhooks/useDomRect";
import { useEffectOnValueChange } from "powerhooks/useEffectOnValueChange";
import { useState, useEffect, useMemo, useReducer, memo } from "react";
import type { ReactNode, RefObject } from "react";
import type { ReturnType } from "tsafe";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";
import { useNonPostableEvtLike } from "../../tools/useNonPostableEvtLike";
import { CircularProgress } from "../CircularProgress";
import { Text } from "../theme";

export type AttributeOption = string | { value: string; label: string };
export type AttributeOptions = AttributeOption[];

export type TextFieldProps = {
  className?: string;
  id?: string;
  name?: string;
  /** Default text */
  type?: "text" | "password" | "email" | "number";
  size?: "small" | "medium";
  InputPropsClass?: {
    className?: string;
  };
  /** Will overwrite value when updated */
  defaultValue?: string;
  inputProps_ref?: RefObject<HTMLInputElement>;
  "inputProps_aria-label"?: string;
  inputProps_tabIndex?: number;
  inputProps_spellCheck?: boolean;
  inputProps_autoFocus?: boolean;
  doIndentOnTab?: boolean;
  /**
   * If true, it sets the helper text in red.
   * Will be set automatically if getIsValidValue is provided
   * */
  "inputProps_aria-invalid"?: boolean;
  InputProps_endAdornment?: ReactNode;
  /** Only use when getIsValidValue isn't used */
  disabled?: boolean;
  /** Return false to e.preventDefault() and e.stopPropagation() */
  onEscapeKeyDown?: (params: { preventDefaultAndStopPropagation(): void }) => void;
  onEnterKeyDown?: (params: { preventDefaultAndStopPropagation(): void }) => void;
  onBlur?: () => void;

  /** To prevent onSubmit to be invoked (when data is being updated for example ) default true*/
  isSubmitAllowed?: boolean;
  evtAction?: NonPostableEvtLike<"TRIGGER SUBMIT" | "RESTORE DEFAULT VALUE">;
  /** Submit invoked on evtAction.post("TRIGGER SUBMIT") only if value being typed is valid */
  onSubmit?: (value: string) => void;
  getIsValidValue?: (
    value: string
  ) => { isValidValue: true } | { isValidValue: false; message: string | ReactNode };
  /**
   * Invoked on first render,
   * called again if getIsValidValue have been updated and
   * the validity of the current value changes.
   */
  onValueBeingTypedChange?: (
    params: { value: string } & ReturnType<TextFieldProps["getIsValidValue"]>
  ) => void;
  transformValueBeingTyped?: (value: string) => string;
  label?: ReactNode;
  helperText?: ReactNode;
  questionMarkHelperText?: string | NonNullable<ReactNode>;
  doOnlyValidateInputAfterFistFocusLost?: boolean;
  /** Default false */
  isCircularProgressShown?: boolean;
  placeholder?: string;
  filled?: boolean;
  hiddenLabel?: boolean;
  selectAllTextOnFocus?: boolean;
  /** Default false */
  doRenderAsTextArea?: boolean;
  /** Only applies if doRenderAsTextArea is true */
  rows?: number;
  /** NOTE: If length 0 it's assumed loading */
  options?: AttributeOptions;
  setValueData?: (string) => void;

  autoComplete?:
    | "on"
    | "off"
    | "name"
    | "honorific-prefix"
    | "given-name"
    | "additional-name"
    | "family-name"
    | "honorific-suffix"
    | "nickname"
    | "email"
    | "username"
    | "new-password"
    | "current-password"
    | "one-time-code"
    | "organization-title"
    | "organization"
    | "street-address"
    | "address-line1"
    | "address-line2"
    | "address-line3"
    | "address-level4"
    | "address-level3"
    | "address-level2"
    | "address-level1"
    | "country"
    | "country-name"
    | "postal-code"
    | "cc-name"
    | "cc-given-name"
    | "cc-additional-name"
    | "cc-family-name"
    | "cc-number"
    | "cc-exp"
    | "cc-exp-month"
    | "cc-exp-year"
    | "cc-csc"
    | "cc-type"
    | "transaction-currency"
    | "transaction-amount"
    | "language"
    | "bday"
    | "bday-day"
    | "bday-month"
    | "bday-year"
    | "sex"
    | "tel"
    | "tel-country-code"
    | "tel-national"
    | "tel-area-code"
    | "tel-local"
    | "tel-extension"
    | "impp"
    | "url"
    | "photo";
};


export const TextField = memo((props: TextFieldProps) => {
  const {
    transformValueBeingTyped,
    defaultValue = "",
    setValueData,
    getIsValidValue,
    doOnlyValidateInputAfterFistFocusLost = true,
    onValueBeingTypedChange,
    onBlur,
    evtAction: evtActionLike,
    onSubmit,
    onEscapeKeyDown,
    onEnterKeyDown,
    className,
    placeholder,
    filled = false,
    hiddenLabel = false,
    type = "text",
    size = "medium",
    isCircularProgressShown = false,
    helperText,
    id: htmlId,
    name,
    selectAllTextOnFocus,
    isSubmitAllowed = true,
    InputPropsClass,
    inputProps_ref,
    "inputProps_aria-label": inputProps_ariaLabel,
    inputProps_tabIndex,
    inputProps_spellCheck,
    inputProps_autoFocus,
    "inputProps_aria-invalid": inputProps_ariaInvalid,
    InputProps_endAdornment,
    questionMarkHelperText,
    doRenderAsTextArea = false,
    rows,
    doIndentOnTab = false,
    options,
    ...completedPropsRest
  } = props;

  const evtAction = useNonPostableEvtLike(evtActionLike);

  const { value, transformAndSetValue } = (function useClosure() {
    const [value, setValue] = useState(defaultValue);

    const transformAndSetValue = useConstCallback((value: string) => {
      if (!isValidationEnabled && !doOnlyValidateInputAfterFistFocusLost) {
        enableValidation();
      }

      setValue(transformValueBeingTyped?.(value) ?? value);
      if (setValueData) {
        setValueData(transformValueBeingTyped?.(value) ?? value);
      }
    });

    return { value, transformAndSetValue };
  })();

  useEffectOnValueChange(() => transformAndSetValue(defaultValue), [defaultValue]);

  const getIsValidValueResult = useMemo(
    () => getIsValidValue?.(value) ?? { isValidValue: true as const },
    [value, getIsValidValue ?? Object]
  );

  useEffect(() => {
    onValueBeingTypedChange?.({ value, ...getIsValidValueResult });
  }, [
    value,
    getIsValidValueResult.isValidValue,
    getIsValidValueResult.isValidValue ? Object : getIsValidValueResult.message,
  ]);

  const [isValidationEnabled, enableValidation] = useReducer(() => true, false);

  useEvt(
    (ctx) =>
      evtAction?.attach(ctx, (action) => {
        switch (action) {
          case "RESTORE DEFAULT VALUE":
            transformAndSetValue(defaultValue);
            return;
          case "TRIGGER SUBMIT":
            if (!getIsValidValueResult.isValidValue || !isSubmitAllowed) {
              return;
            }
            onSubmit?.(value);
            return;
        }
      }),
    [
      defaultValue,
      value,
      getIsValidValueResult,
      onSubmit ?? Object,
      evtAction ?? Object,
      transformAndSetValue,
      isSubmitAllowed,
    ]
  );

  const hasError =
    inputProps_ariaInvalid ?? (isValidationEnabled ? !getIsValidValueResult.isValidValue : false);

  const {
    domRect: { height: rootHeight },
    ref,
  } = useDomRect();

  const { classes, cx } = useStyles({
    hasError,
    rootHeight,
    filled,
  });

  const [isPasswordShown] = useReducer((v: boolean) => !v, false);

  const onKeyDown = useConstCallback(
    (event: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement | HTMLDivElement>) => {
      const key = (() => {
        switch (event.key) {
          case "Tab":
            return doIndentOnTab ? event.key : "irrelevant";
          case "Escape":
          case "Enter":
            return event.key;

          default:
            return "irrelevant";
        }
      })();

      if (key === "irrelevant") {
        return;
      }

      const preventDefaultAndStopPropagation = () => {
        event.preventDefault();
        event.stopPropagation();
      };

      switch (key) {
        case "Escape":
          onEscapeKeyDown?.({ preventDefaultAndStopPropagation });
          return;
        case "Enter":
          onEnterKeyDown?.({ preventDefaultAndStopPropagation });
          return;
        case "Tab":
          document.execCommand("insertText", false, "    ");
          preventDefaultAndStopPropagation();
          return;
      }

      assert<Equals<typeof key, never>>();
    }
  );

  const InputProps = useMemo(
    () => ({
      // startAdornment: iconId ? (
      //   <InputAdornment position="start">
      //     {/* <NormalIcon iconId={iconId} iconVariant="gray" /> */}
      //   </InputAdornment>
      // ) : null,
      endAdornment:
        InputProps_endAdornment ?? isCircularProgressShown ? (
          <InputAdornment position="end">
            <CircularProgress color="textPrimary" size={10} />
          </InputAdornment>
        ) : type === "password" ? (
          <InputAdornment position="end">
            {/* <IconButton
              iconId={isPasswordShown ? "visibilityOff" : "visibility"}
              onClick={toggleIsPasswordShown}
            /> */}
          </InputAdornment>
        ) : undefined,
    }),
    [isPasswordShown, type, InputProps_endAdornment, isCircularProgressShown]
  );

  const inputProps = useMemo(
    () => ({
      className: InputPropsClass?.className,
      ref: inputProps_ref,
      "aria-label": inputProps_ariaLabel,
      tabIndex: inputProps_tabIndex,
      spellCheck: inputProps_spellCheck,
      autoFocus: inputProps_autoFocus,
      ...(inputProps_ariaInvalid !== undefined
        ? {
            "aria-invalid": inputProps_ariaInvalid,
          }
        : hasError
        ? { "aria-invalid": true }
        : {}),
    }),
    [
      inputProps_ref ?? Object,
      inputProps_ariaLabel ?? Object,
      inputProps_tabIndex ?? Object,
      inputProps_spellCheck ?? Object,
      inputProps_autoFocus ?? Object,
      inputProps_ariaInvalid ?? Object,
      hasError,
    ]
  );

  const onMuiTextfieldBlur = useConstCallback(() => {
    if (!isValidationEnabled) enableValidation();
    onBlur?.();
  });
  const onFocus = useConstCallback(
    ({ target }: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      if (!selectAllTextOnFocus) return;
      target.setSelectionRange(0, target.value.length);
    }
  );

  const onChange = useConstCallback(({ target }: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    transformAndSetValue(target.value)
  );

  const helperTextNode = (
    <Text className={classes.helperText} typo="caption" htmlComponent="span">
      {isValidationEnabled && !getIsValidValueResult.isValidValue
        ? getIsValidValueResult.message || helperText
        : helperText}
      &nbsp;
    </Text>
  );

  return (
    <MuiTextField
      className={cx(classes.muiTextField, className)}
      sx={{
        borderBottom: "none",
      }}
      multiline={doRenderAsTextArea}
      rows={!doRenderAsTextArea ? undefined : rows}
      ref={ref}
      hiddenLabel={hiddenLabel}
      variant={filled ? "filled" : "outlined"}
      type={type !== "password" ? type : isPasswordShown ? "text" : "password"}
      value={value}
      select={options !== undefined}
      error={hasError}
      helperText={helperTextNode}
      InputProps={InputProps}
      size={size}
      onBlur={onMuiTextfieldBlur}
      onChange={onChange}
      placeholder={placeholder}
      onKeyDown={onKeyDown}
      onFocus={onFocus}
      id={htmlId}
      name={name}
      inputProps={inputProps}
      SelectProps={{
        sx: {
          maxHeight: "350px",
        },
      }}
      {...completedPropsRest}>
      {options !== undefined &&
        options.map((option: string | AttributeOption) => {
          if (typeof option === "string") {
            return (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            );
          } else {
            return (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            );
          }
        })}
    </MuiTextField>
  );
});

const useStyles = makeStyles<{
  hasError: boolean;
  rootHeight: number;
  filled: boolean;
}>({
  name: { TextField },
})((theme, { hasError, rootHeight, filled }) => ({
  muiAutocomplete: {
    minWidth: 145,
    color: "red",
  },
  muiTextField: {
    "& .MuiFormHelperText-root": {
      position: "absolute",
      top: rootHeight,
      visibility: rootHeight === 0 ? "hidden" : undefined,
    },
    "& .MuiFormLabel-root": {
      color: hasError
        ? theme.colors.useCases.alertSeverity.error.main
        : theme.colors.useCases.typography.textSecondary,
    },
    "&:focus": {
      outline: "unset",
    },
    "& .MuiInput-underline:hover:not(.Mui-disabled):before": {
      borderBottomWidth: filled ? 0 : 1,
    },
    "& .MuiInput-underline:after": {
      borderBottomWidth: filled ? 0 : 1,
    },
    "& .mui-1ab69dk-MuiInputBase-root-MuiFilledInput-root:before": {
      border: "none",
    },
    "& .mui-1ab69dk-MuiInputBase-root-MuiFilledInput-root:hover:not(.Mui-disabled, .Mui-error):before": {
      border: "none",
    },
    "& .mui-1ab69dk-MuiInputBase-root-MuiFilledInput-root:after": {
      border: "none",
    },
    "& .mui-13cia9v-MuiInputBase-root-MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline": {
      borderColor: `${theme.colors.palette.dark.main}80`,
    },
    "& .mui-13cia9v-MuiInputBase-root-MuiOutlinedInput-root.Mui-disabled .MuiOutlinedInput-notchedOutline": {
      borderColor: `${theme.colors.palette.dark.main}29`,
    },
    "& .mui-5hs7hk-MuiFormLabel-root-MuiInputLabel-root.Mui-disabled": {
      color: `${theme.colors.palette.dark.main}29`,
    },
    "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
      borderColor: theme.colors.palette.focus.main,
    },
  },
  helperText: {
    color: hasError
      ? theme.colors.useCases.alertSeverity.error.main
      : theme.colors.useCases.typography.textDisabled,
    whiteSpace: "nowrap",
  },
  questionMark: {
    fontSize: "inherit",
    ...(() => {
      const factor = 1.5;

      return {
        width: `${factor}em`,
        height: `${factor}em`,
      };
    })(),
  },
}));
