'use client'

import * as React from 'react';
import { ToggleButtonGroup, ToggleButton } from '@mui/material';

export type ToggleButtonsType = {
  items?: {
    icon: React.ReactNode;
    value: string;
  }[];
  className?: string;
  val: string;
  setVal: any;
}

export default function ToggleButtons(props: ToggleButtonsType) {
  const {
    className,
    items,
    val,
    setVal
  } = props;

  return (
    <ToggleButtonGroup
      color="primary"
      value={val}
      exclusive
      onChange={(e, newVal) => setVal(newVal)}
      aria-label="Platform"
      className={className || ''}
    >
      {items?.map(item => <ToggleButton value={item.value}>{item.icon}</ToggleButton>)}
    </ToggleButtonGroup>
  );
}
