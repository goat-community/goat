// Copyright (c) 2020 GitHub user u/garronej
import { TabList, TabPanel, TabContext } from "@mui/lab";
import { Box, Tab } from "@mui/material";
import { forwardRef, memo } from "react";
import React, { useState } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";

export type SlideShowProps = {
  className?: string;
  tabs: {
    child: React.ReactNode;
    name: string;
  }[];
};

export const Tabs = memo(
  forwardRef<HTMLElement, SlideShowProps>((props, ref) => {
    const {
      className,
      tabs,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    const { classes } = useStyles();

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    // Component States
    const [value, setValue] = useState("1");

    // functions
    const handleChange = (event: React.SyntheticEvent, newValue: string) => {
      setValue(newValue);
    };

    return (
      <Box sx={{ width: "100%", typography: "14px" }} className={className}>
        <TabContext initialSelectedIndex="1" value={value}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <TabList onChange={handleChange} aria-label="lab API tabs example">
              {tabs.map((tab, index) => (
                <Tab label={tab.name} value={`${index + 1}`} key={index} className={classes.tab} />
              ))}
            </TabList>
          </Box>
          {tabs.map((tab, index) => (
            <TabPanel value={`${index + 1}`} key={index} className={classes.tabPandel}>
              {tab.child}
            </TabPanel>
          ))}
        </TabContext>
      </Box>
    );
  })
);

const useStyles = makeStyles({ name: { Tabs } })((theme) => ({
  tab: {
    padding: theme.spacing(2),
    fontSize: "14px",
  },
  tabPandel: {
    padding: "0",
    paddingTop: theme.spacing(3),
  },
}));
