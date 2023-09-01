import { FormControl, MenuItem, Select, Typography } from "@mui/material";
import BasicAccordion from "@p4b/ui/components/BasicAccordion";

import React from "react";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";

const Marker = () => {
  return (
    <BasicAccordion title="Marker" variant="secondary">
      <FormControl sx={{ m: 1, width: "100%" }}>
        <Select size="small">
          <MenuItem>
            <Icon iconName={ICON_NAME.STAR} fontSize="small" />
            <Typography variant="body2">Icon</Typography>
          </MenuItem>
          <MenuItem>
            <Icon iconName={ICON_NAME.CIRCLE} fontSize="small" />
            <Typography variant="body2">Shape</Typography>
          </MenuItem>
        </Select>
      </FormControl>
    </BasicAccordion>
  );
};

export default Marker;
