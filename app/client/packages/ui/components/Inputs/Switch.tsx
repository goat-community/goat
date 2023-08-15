import { Switch as MUISwitch } from "@mui/material";

interface SwitchProps {
  defaultChecked?: boolean;
  elementName?: string;
  checked: boolean;
  onChecked: (event: React.ChangeEvent<HTMLInputElement>, checked: boolean, elementName?: string) => void;
  disabled?: boolean;
}

/**
 * A custom switch component.
 * @param {SwitchProps} props - The props for the switch component.
 * @returns The switch component.
 */

export const Switch = (props: SwitchProps) => {
  const { checked, onChecked, elementName, disabled = false } = props;

  return (
    <MUISwitch
      checked={checked}
      disabled={disabled}
      onChange={(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) =>
        onChecked(event, checked, elementName ? elementName : "")
      }
      aria-label="Switch demo"
    />
  );
};
