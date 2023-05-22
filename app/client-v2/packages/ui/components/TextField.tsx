// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable react-hooks/exhaustive-deps */

/* eslint-disable react/display-name */
import Help from "@mui/icons-material/Help";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import Autocomplete from "@mui/material/Autocomplete";
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

import { makeStyles } from "../lib/ThemeProvider";
import { getBrowser } from "../tools/getBrowser";
import { useNonPostableEvtLike } from "../tools/useNonPostableEvtLike";
import { CircularProgress } from "./CircularProgress";
import { createIcon } from "./Icon/Icon";
import { createIconButton } from "./IconButton";
import { Text } from "./Text/TextBase";
import { Tooltip } from "./Tooltip";

export type TextFieldProps = {
  className?: string;
  id?: string;
  name?: string;
  /** Default text */
  type?: "text" | "password" | "email";
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
  selectAllTextOnFocus?: boolean;
  /** Default false */
  doRenderAsTextArea?: boolean;
  /** Only applies if doRenderAsTextArea is true */
  rows?: number;
  /** NOTE: If length 0 it's assumed loading */
  options?: string[];

  //NOTE: freeSolo only takes effects if options is provided.
  freeSolo?: boolean;

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

const { Icon } = createIcon({
  visibilityOff: VisibilityOff,
  visibility: Visibility,
  help: Help,
});

const { IconButton } = createIconButton({ Icon });

export const TextField = memo((props: TextFieldProps) => {
  const {
    transformValueBeingTyped,
    defaultValue = "",
    getIsValidValue,
    doOnlyValidateInputAfterFistFocusLost = true,
    onValueBeingTypedChange,
    onBlur,
    evtAction: evtActionLike,
    onSubmit,
    onEscapeKeyDown,
    onEnterKeyDown,
    className,
    type = "text",
    isCircularProgressShown = false,
    helperText,
    id: htmlId,
    name,
    selectAllTextOnFocus,
    isSubmitAllowed = true,
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
    freeSolo = false,
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
  });

  const [isPasswordShown, toggleIsPasswordShown] = useReducer((v: boolean) => !v, false);

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
      endAdornment:
        InputProps_endAdornment ?? isCircularProgressShown ? (
          <InputAdornment position="end">
            <CircularProgress color="textPrimary" size={10} />
          </InputAdornment>
        ) : type === "password" ? (
          <InputAdornment position="end">
            <IconButton
              iconId={isPasswordShown ? "visibilityOff" : "visibility"}
              onClick={toggleIsPasswordShown}
            />
          </InputAdornment>
        ) : undefined,
    }),
    [isPasswordShown, type, InputProps_endAdornment, isCircularProgressShown]
  );

  const inputProps = useMemo(
    () => ({
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

  const onInputChange = useConstCallback((_: any, value: string) => transformAndSetValue(value));
  const onChange = useConstCallback(({ target }: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    transformAndSetValue(target.value)
  );

  const helperTextNode = (
    <Text className={classes.helperText} typo="caption" htmlComponent="span">
      {isValidationEnabled && !getIsValidValueResult.isValidValue
        ? getIsValidValueResult.message || helperText
        : helperText}
      &nbsp;
      {questionMarkHelperText !== undefined && (
        <Tooltip title={questionMarkHelperText}>
          <Icon iconId="help" className={classes.questionMark} />
        </Tooltip>
      )}
    </Text>
  );

  if (options !== undefined) {
    assert(type === "text");

    return (
      <Autocomplete
        freeSolo={freeSolo}
        className={cx(classes.muiAutocomplete, className)}
        inputValue={value}
        onInputChange={onInputChange}
        options={options}
        id={htmlId}
        renderInput={(params) => (
          <MuiTextField
            {...params}
            className={classes.muiTextField}
            multiline={doRenderAsTextArea}
            ref={ref}
            variant="standard"
            error={hasError}
            helperText={helperTextNode}
            InputProps={{ ...params.InputProps, ...InputProps }}
            onBlur={onMuiTextfieldBlur}
            onKeyDown={onKeyDown}
            onFocus={onFocus}
            name={name}
            inputProps={{ ...inputProps, ...params.inputProps }}
            {...completedPropsRest}
          />
        )}
      />
    );
  }

  return (
    <MuiTextField
      className={cx(classes.muiTextField, className)}
      multiline={doRenderAsTextArea}
      rows={!doRenderAsTextArea ? undefined : rows}
      ref={ref}
      variant="standard"
      type={type !== "password" ? type : isPasswordShown ? "text" : "password"}
      value={value}
      error={hasError}
      helperText={helperTextNode}
      InputProps={InputProps}
      onBlur={onMuiTextfieldBlur}
      onChange={onChange}
      onKeyDown={onKeyDown}
      onFocus={onFocus}
      id={htmlId}
      name={name}
      inputProps={inputProps}
      {...completedPropsRest}
    />
  );
});

const useStyles = makeStyles<{
  hasError: boolean;
  rootHeight: number;
}>({
  name: { TextField },
})((theme, { hasError, rootHeight }) => ({
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
    "& input:-webkit-autofill": {
      ...(() => {
        switch (getBrowser()) {
          case "chrome":
          case "safari":
            return {
              WebkitTextFillColor:
                theme.colors.useCases.typography[theme.isDarkModeEnabled ? "textPrimary" : "textSecondary"],
              WebkitBoxShadow: `0 0 0 1000px ${theme.colors.useCases.surfaces.surface1} inset`,
            };
          default:
            return {};
        }
      })(),
    },
    "& .MuiInput-underline:hover:not(.Mui-disabled):before": {
      borderBottomWidth: 1,
    },
    "& .MuiInput-underline:after": {
      borderBottomWidth: 1,
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
