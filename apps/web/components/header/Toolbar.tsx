"use client";

import {
  AppBar,
  Box,
  Divider,
  IconButton,
  Link,
  Toolbar as MUIToolbar,
  Stack,
  useTheme,
} from "@mui/material";
import React from "react";

import { GOATLogoIconOnlyGreen } from "@p4b/ui/assets/svg/GOATLogoIconOnlyGreen";
import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

export type MapToolbarProps = {
  LeftToolbarChild?: React.ReactNode;
  RightToolbarChild?: React.ReactNode;
  height: number;
  showHambugerMenu?: boolean;
  onMenuIconClick?: () => void;
};

export function Toolbar(props: MapToolbarProps) {
  const { LeftToolbarChild, RightToolbarChild, height, showHambugerMenu, onMenuIconClick } = props;

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
            <IconButton onClick={onMenuIconClick}>
              <Icon iconName={ICON_NAME.HAMBURGER_MENU} fontSize="inherit" />
            </IconButton>

            <Divider orientation="vertical" flexItem sx={{ ml: 2, mr: 3 }} />
          </>
        )}

        <Link
          href="/home"
          style={{
            width: "32px",
            height: "32px",
            cursor: "pointer",
          }}>
          <Box
            sx={{
              transition: "transform 0.2s ease-in-out",
              "&:hover": {
                transform: "scale(1.1)",
              },
            }}>
            <GOATLogoIconOnlyGreen style={{ width: "32px", height: "32px", cursor: "pointer" }} />
          </Box>
        </Link>

        <Stack
          direction="row"
          alignItems="center"
          sx={{
            mx: theme.spacing(2),
            gap: theme.spacing(2),
          }}>
          {LeftToolbarChild}
        </Stack>
        <Box sx={{ flexGrow: 1 }} />

        {RightToolbarChild}
      </MUIToolbar>
    </AppBar>
  );
}
