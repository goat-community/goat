"use client";

import { makeStyles } from "@/lib/theme";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { Button, List, ListItem, ListItemButton, ListItemIcon, Typography } from "@mui/material";
import { useState } from "react";
import * as React from "react";
import { v4 } from "uuid";

import Box from "@p4b/ui/components/Box";
import type { IconId } from "@p4b/ui/components/theme";
import { Icon, IconButton } from "@p4b/ui/components/theme";

import Layer from "./Layer";

export type IStylingSideBarProps = {
  width: number;
  extended_width: number;
  children: React.ReactNode;
};

const items: { icon: IconId; value: string }[] = [
  {
    icon: "fileInfo",
    value: "File Info",
  },
  {
    icon: "slider",
    value: "Slider",
  },
  {
    icon: "colorLens",
    value: "Layer design",
  },
  {
    icon: "print",
    value: "Print",
  },
];

function StylingSideBar(props: IStylingSideBarProps) {
  const { children } = props;

  const { classes, cx } = useStyles(props)();

  const [activeOption, setActiveOption] = useState<string | null>(null);

  const handleIconClick = (value: string) => {
    setActiveOption(value);
  };

  return (
    <>
      <nav className={cx(classes.root)}>
        <List className={cx(classes.itemContainer)}>
          {items?.map(({ icon, value }) => (
            <Box key={v4()}>
              <ListItem disablePadding>
                <ListItemButton
                  className={cx(classes.itemList, activeOption === value && classes.activeIcon)}
                  onClick={() => handleIconClick(value)}>
                  <ListItemIcon>
                    <Icon
                      size="default"
                      iconId={icon}
                      iconVariant={activeOption === value ? "focus" : "gray"}
                    />
                  </ListItemIcon>
                </ListItemButton>
              </ListItem>
            </Box>
          ))}
        </List>
      </nav>
      {children}
      {activeOption && (
        <Box className={cx(classes.activeContent)}>
          <Box className={cx(classes.contentHeading)}>
            <IconButton iconId="chevronRight" iconVariant="focus" onClick={() => setActiveOption(null)} />
            <Typography color="#2BB381" variant="body1">
              {activeOption}
            </Typography>
          </Box>
          <Box className={cx(classes.contentInfo)}>{activeOption === "Layer design" && <Layer />}</Box>
          <Box className={cx(classes.buttonsContainer)}>
            <Button className={cx(classes.button)} color="secondary" variant="outlined" disabled>
              Reset
            </Button>
            <Button
              className={cx(classes.button)}
              color="primary"
              variant="outlined"
              disabled
              endIcon={<ArrowDropDownIcon />}>
              Save As
            </Button>
          </Box>
        </Box>
      )}
    </>
  );
}

const useStyles = (props: IStylingSideBarProps) =>
  makeStyles({ name: { StylingSideBar } })((theme) => ({
    root: {
      zIndex: "20",
      paddingTop: "52px",
      backgroundColor: theme.colors.useCases.surfaces.surface2,
      cursor: "pointer",
      width: props.width,
      right: 0,
      top: 0,
      bottom: 0,
      position: "fixed",
      transition: "width 0.4s ease",
      display: "flex",
      overflow: "hidden",
      flexDirection: "column",
      boxShadow: "0px 1px 5px 0px #0000001F, 0px 2px 2px 0px #00000024, 0px 3px 1px -2px #00000033",
    },
    itemContainer: {
      display: "flex",
      flexDirection: "column",
      rowGap: "16px",
    },
    itemList: {
      "&:hover": {
        backgroundColor: `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant2}aa`,
      },
    },
    activeIcon: {
      backgroundColor: `${theme.colors.palette.focus}aa`,
    },
    activeContent: {
      width: props.extended_width,
      backgroundColor: theme.colors.useCases.surfaces.surface2,
      position: "fixed",
      marginRight: props.width,
      right: 0,
      top: 0,
      bottom: 0,
      zIndex: "10",
      boxShadow: "0px 1px 5px 0px #0000001F, 0px 2px 2px 0px #00000024, 0px 3px 1px -2px #00000033",
      paddingTop: "52px",
    },
    contentHeading: {
      display: "flex",
      columnGap: "8px",
      alignItems: "center",
      padding: "12px 16px",
    },
    buttonsContainer: {
      padding: "16px",
      display: "flex",
      columnGap: "16px",
      position: "absolute",
      bottom: 0,
      width: "100%",
    },
    button: {
      borderRadius: "24px",
      textTransform: "none",
      fontSize: "14px",
      width: "50%",
      "&:disabled": {
        border: "1px solid #ccc",
        backgroundColor: "#f5f5f5",
        color: "#888",
      },
    },
    contentInfo: {},
  }));

export default StylingSideBar;
