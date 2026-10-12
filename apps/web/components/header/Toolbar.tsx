"use client";

import { AppBar, Divider, IconButton, Toolbar as MUIToolbar, Stack, useTheme } from "@mui/material";
import React from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

export type MapToolbarProps = {
  LeftToolbarChild?: React.ReactNode;
  CenterToolbarChild?: React.ReactNode;
  RightToolbarChild?: React.ReactNode;
  height: number;
  showHambugerMenu?: boolean;
  onMenuIconClick?: () => void;
};

export function Toolbar(props: MapToolbarProps) {
  const {
    LeftToolbarChild,
    CenterToolbarChild,
    RightToolbarChild,
    height,
    showHambugerMenu,
    onMenuIconClick,
  } = props;

  const theme = useTheme();

  return (
    <AppBar
      position="relative"
      elevation={0}
      color="primary"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 2,
        borderBottom: "1px solid rgba(58, 53, 65, 0.12)",
      }}>
      <MUIToolbar
        variant="dense"
        sx={{
          minHeight: height,
          height: height,
          boxShadow: "0px 0px 10px 0px rgba(58, 53, 65, 0.1)",
        }}>
        {showHambugerMenu && (
          <>
            {/* Shown below md by CSS so the server-rendered HTML is right before hydration. */}
            <IconButton onClick={onMenuIconClick} sx={{ display: { xs: "inline-flex", md: "none" } }}>
              <Icon iconName={ICON_NAME.HAMBURGER_MENU} fontSize="inherit" />
            </IconButton>

            <Divider
              orientation="vertical"
              flexItem
              sx={{ ml: 2, mr: 3, display: { xs: "block", md: "none" } }}
            />
          </>
        )}

        {/* Three columns rather than an absolutely-centred middle: the side columns
            share the leftover space equally, which keeps the centre child centred
            while letting the sides shrink and truncate instead of sliding underneath it. */}
        <Stack
          direction="row"
          alignItems="center"
          sx={{
            gap: theme.spacing(2),
            flex: "1 1 0",
            minWidth: 0,
            overflow: "hidden",
            whiteSpace: "nowrap",
          }}>
          {LeftToolbarChild}
        </Stack>

        {CenterToolbarChild && (
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="center"
            sx={{
              flex: "0 0 auto",
              mx: theme.spacing(2),
            }}>
            {CenterToolbarChild}
          </Stack>
        )}

        <Stack
          direction="row"
          alignItems="center"
          justifyContent="flex-end"
          sx={{
            flex: "1 1 0",
            minWidth: 0,
          }}>
          {RightToolbarChild}
        </Stack>
      </MUIToolbar>
    </AppBar>
  );
}
