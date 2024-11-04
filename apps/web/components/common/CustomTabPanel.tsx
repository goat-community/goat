import { Box } from "@mui/material";

export function a11yProps(value: string) {
  return {
    id: `simple-tab-${value}`,
    "aria-controls": `simple-tabpanel-${value}`,
  };
}

export interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
  disablePadding?: boolean;
}

export function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, disablePadding, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}>
      {value === index && <Box sx={{ p: disablePadding ? 0 : 3 }}>{children}</Box>}
    </div>
  );
}
