import { FormControl, MenuItem, Select, Typography } from "@mui/material";
import BasicAccordion from "@p4b/ui/components/BasicAccordion";

import React from "react";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { makeStyles } from "@/lib/theme";
import { useTheme } from "@p4b/ui/components/theme";

const MarkerOptionSymbol = () => {
  const { classes } = useStyles();
  const theme = useTheme();
  return (
    <BasicAccordion title="Marker" variant="secondary">
      <FormControl sx={{ m: 1, width: "100%" }}>
        <Select size="small" className={classes.select}>
          <MenuItem value="icon" className={classes.menuItem}>
            <Icon
              iconName={ICON_NAME.STAR}
              htmlColor={theme.colors.palette.focus.main}
              fontSize="small"
            />
            <Typography variant="body2">Icon</Typography>
          </MenuItem>
          <MenuItem value="shape" className={classes.menuItem}>
            <Icon
              iconName={ICON_NAME.CIRCLE}
              htmlColor={theme.colors.palette.focus.main}
              fontSize="small"
            />
            <Typography variant="body2">Shape</Typography>
          </MenuItem>
        </Select>
      </FormControl>
    </BasicAccordion>
  );
};

const useStyles = makeStyles({ name: { MarkerOptionSymbol } })(() => ({
  select: {
    "& .MuiSelect-select": {
      display: "flex",
      columnGap: "8px",
      alignItems: "center",
    },
  },
  menuItem: {
    display: "flex",
    columnGap: "8px",
    alignItems: "center",
  },
}));

export default MarkerOptionSymbol;
