"use client";

import { ToggleButtonGroup, ToggleButton } from "@mui/material";
import * as React from "react";

export type ToggleButtonsType = {
  items?: {
    icon: React.ReactNode;
    value: string;
  }[];
  className?: string;
  val: string;
  setVal: any;
};

export default function ToggleButtons(props: ToggleButtonsType) {
  const { className, items, val, setVal } = props;

  return (
    <ToggleButtonGroup
      color="secondary"
      value={val}
      exclusive
      onChange={(_, newVal) => setVal(newVal)}
      aria-label="Platform"
      className={className || ""}>
      {items?.map((item) => (
        <ToggleButton key={`toggleButton-${item.value}`} value={item.value}>
          {item.icon}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  );
}
