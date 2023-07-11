import { Switch as MUISwitch } from "@mui/material";
import * as React from "react";

interface SwitchProps {
  defaultChecked?: boolean;
  checked: boolean;
  onChecked: (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => void;
}

const Switch = (props: SwitchProps) => {
  const { defaultChecked = false, checked, onChecked } = props;

  return (
    <MUISwitch
      checked={checked}
      onChange={onChecked}
      aria-label="Switch demo"
      defaultChecked={defaultChecked}
    />
  );
};

export default Switch;
