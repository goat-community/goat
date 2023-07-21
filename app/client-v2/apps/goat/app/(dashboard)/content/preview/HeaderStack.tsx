"use client";

import { makeStyles } from "@/lib/theme";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BackupTableIcon from "@mui/icons-material/BackupTable";
import ColorLensIcon from "@mui/icons-material/ColorLens";
import MapIcon from "@mui/icons-material/Map";
import { Button, Stack, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { useState } from "react";

import Box from "@p4b/ui/components/Box";
import BasicBreadcrumbs from "@p4b/ui/components/BreadCrumbs";
import ToggleButtons from "@p4b/ui/components/ToggleButtons";

const useStyles = makeStyles({ name: { HeaderStack } })((theme) => ({
  header: {
    backgroundColor: theme.muiTheme.palette.background.paper,
    height: "56px",
    padding: theme.spacing(4),
    zIndex: "100",
    boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
  },
  title: {
    fontSize: "24px",
    fontStyle: "normal",
    fontWeight: 800,
    lineHeight: "133.4%",
    color: "#09241A",
  },
  breadcrumbsWrapper: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  },
}));

export default function HeaderStack() {
  const [mode, setMode] = useState("map");
  const { classes, cx } = useStyles();

  const router = useRouter();

  const buttons = [
    {
      icon: <MapIcon sx={{ color: "#09241A" }} />,
      value: "map",
    },
    {
      icon: <BackupTableIcon sx={{ color: "#09241A" }} />,
      value: "table",
    },
    {
      icon: <ColorLensIcon sx={{ color: "#09241A" }} />,
      value: "colorLens",
    },
  ];

  const handleChangeBreadCrumb = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.preventDefault();
    console.info("You clicked a breadcrumb.");
  };

  const returnHandler = () => {
    router.push("/home");
  };

  return (
    <Stack className={cx(classes.header)} direction="row" justifyContent="space-between" alignItems="center">
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ paddingY: "6px", width: "100%" }}>
        <Typography className={cx(classes.title)}>Preview</Typography>
        <Box className={cx(classes.breadcrumbsWrapper)}>
          <Button onClick={returnHandler} startIcon={<ArrowBackIcon color="primary" />}>
            Return
          </Button>
          <BasicBreadcrumbs eventHandler={handleChangeBreadCrumb} />
        </Box>
        <ToggleButtons val={mode} setVal={setMode} items={buttons} />
      </Stack>
    </Stack>
  );
}
