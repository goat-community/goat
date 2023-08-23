// Copyright (c) 2020 GitHub user u/garronej
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { forwardRef, memo } from "react";
import React, { useState } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";
import { v4 } from "uuid";

import { makeStyles } from "../../lib/ThemeProvider";
import { Icon } from "../theme";
import type { IconId } from "../theme";

export type ToggleTabsProps = {
  className?: string;
  onResultChange: (value: string | null) => void;
  defaultValue: string | null;
  tabs: {
    iconId: IconId;
    value: string;
  }[];
};

export const ToggleTabs = memo(
  forwardRef<HTMLElement, ToggleTabsProps>((props, ref) => {
    const {
      className,
      tabs,
      defaultValue,
      onResultChange,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    const { classes } = useStyles();

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    // Component States
    const [value, setValue] = useState("1");

    // Functions
    const handleChange = (_: React.SyntheticEvent, newValue: string) => {
      onResultChange(newValue);
    };

    return (
      <ToggleButtonGroup value={defaultValue ? defaultValue : ""} exclusive onChange={handleChange}>
        {tabs.map((tab, index) => (
          <ToggleButton key={v4()} value={tab.value} aria-label="list">
            <Icon iconVariant="gray" iconId={tab.iconId} />
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    );
  })
);

const useStyles = makeStyles({ name: { ToggleTabs } })((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
}));
