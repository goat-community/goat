// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable react/display-name */
import MuiCheckbox from "@mui/material/Checkbox";
import type { CheckboxProps as MuiCheckboxProps } from "@mui/material/Checkbox";
import { useConstCallback } from "powerhooks/useConstCallback";
import { useState, useEffect, memo } from "react";

export type CheckboxProps = MuiCheckboxProps;

export const Checkbox = memo((props: CheckboxProps) => {
  const { defaultChecked: props_defaultChecked, ...rest } = props;

  const defaultChecked = rest.checked === undefined ? false : props_defaultChecked ?? false;

  const [isChecked, setIsChecked] = useState(defaultChecked);

  useEffect(() => setIsChecked(defaultChecked), [defaultChecked]);

  const onChange = useConstCallback<CheckboxProps["onChange"]>((event, checked) => {
    setIsChecked(checked);

    rest.onChange?.(event, checked);
  });

  return (
    <MuiCheckbox
      {...rest}
      {...(rest.checked !== undefined
        ? {
            value: rest.checked ? "on" : "off",
          }
        : {
            checked: isChecked,
            onChange,
            value: isChecked ? "on" : "off",
          })}
    />
  );
});
