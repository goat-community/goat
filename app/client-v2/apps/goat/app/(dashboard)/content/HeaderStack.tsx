"use client";

import { makeStyles } from "@/lib/theme";
import BackupTableIcon from "@mui/icons-material/BackupTable";
import ColorLensIcon from "@mui/icons-material/ColorLens";
import MapIcon from "@mui/icons-material/Map";
import { Stack } from "@mui/material";
import { useState } from "react";

import Box from "@p4b/ui/components/Box";
import BasicBreadcrumbs from "@p4b/ui/components/BreadCrumbs";
import ToggleButtons from "@p4b/ui/components/ToggleButtons";

const useStyles = () =>
  makeStyles({ name: { HeaderStack } })((theme) => ({
    header: {
      backgroundColor: theme.muiTheme.palette.background.paper,
      height: "56px",
      padding: theme.spacing(4),
      zIndex: "100",
      boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
    },
  }));

export default function HeaderStack() {
  const [mode, setMode] = useState("map");
  const { classes, cx } = useStyles()();
  // const theme = useTheme();

  const buttons = [
    {
      icon: <MapIcon />,
      value: "map",
    },
    {
      icon: <BackupTableIcon />,
      value: "table",
    },
    {
      icon: <ColorLensIcon />,
      value: "colorLens",
    },
  ];

  const handleChangeBreadCrumb = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.preventDefault();
    console.info("You clicked a breadcrumb.");
  };

  return (
    <Stack className={cx(classes.header)} direction="row" justifyContent="space-between" alignItems="center">
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ paddingY: "6px", width: "100%" }}>
        <Box>Preview</Box>
        <BasicBreadcrumbs eventHandler={handleChangeBreadCrumb} />
        <ToggleButtons val={mode} setVal={setMode} items={buttons} />
      </Stack>
    </Stack>
  );
}
