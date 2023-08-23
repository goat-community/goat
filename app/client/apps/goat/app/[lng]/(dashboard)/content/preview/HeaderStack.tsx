"use client";

import { setPreviewMode } from "@/lib/store/content/slice";
import { makeStyles } from "@/lib/theme";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BackupTableIcon from "@mui/icons-material/BackupTable";
import MapIcon from "@mui/icons-material/Map";
import { Button, Stack, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";

import Box from "@p4b/ui/components/Box";
import BasicBreadcrumbs from "@p4b/ui/components/BreadCrumbs";
import ToggleButtons from "@p4b/ui/components/ToggleButtons";
import type {IStore} from "@/types/store";

function HeaderStack() {
  const { previewMode } = useSelector((state: IStore) => state.content);

  const router = useRouter();
  const dispatch = useDispatch();
  const { classes, cx } = useStyles();

  const buttons = [
    {
      icon: <MapIcon sx={{ color: "#09241A" }} />,
      value: "map",
    },
    {
      icon: <BackupTableIcon sx={{ color: "#09241A" }} />,
      value: "table",
    },
    // {
    //   icon: <ColorLensIcon sx={{ color: "#09241A" }} />,
    //   value: "styling",
    // },
  ];

  const handleChangeBreadCrumb = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.preventDefault();
    console.info("You clicked a breadcrumb.");
  };

  const returnHandler = () => {
    router.push("/content");
  };

  const setModeHandler = (val: string) => {
    dispatch(setPreviewMode(val));
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
        <ToggleButtons val={previewMode} setVal={setModeHandler} items={buttons} />
      </Stack>
    </Stack>
  );
}

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

export default HeaderStack;
