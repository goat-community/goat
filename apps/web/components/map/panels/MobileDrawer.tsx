import { Global } from "@emotion/react";
import { Box, Button, CssBaseline, SwipeableDrawer, styled, useTheme } from "@mui/material";
import { grey } from "@mui/material/colors";
import React from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import LayerMobile from "./mobile/LayerMobile";
import LegendMobile from "./mobile/LegendMobile";

const drawerBleeding = 56;

interface MobileDrawerProps {
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window?: () => Window;
}

const Root = styled("div")(({ theme }) => ({
  height: "100%",
  backgroundColor: theme.palette.mode === "light" ? grey[100] : theme.palette.background.default,
}));

const DrawerBox = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.default,
  height: `${drawerBleeding}px`,
  position: "absolute",
  top: -drawerBleeding + 1,
  borderTopLeftRadius: 8,
  borderTopRightRadius: 8,
  visibility: "visible",
  right: 0,
  left: 0,
}));

// const Puller = styled(Box)(({ theme }) => ({
//   width: 30,
//   height: 6,
//   backgroundColor: theme.palette.mode === "light" ? grey[300] : grey[900],
//   borderRadius: 3,
//   position: "absolute",
//   top: 8,
//   left: "calc(50% - 15px)",
// }));

const MobileDrawer = (props: MobileDrawerProps) => {
  const { window } = props;
  const [open, setOpen] = React.useState(false);

  const theme = useTheme();

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };

  const container = window !== undefined ? () => window().document.body : undefined;

  return (
    <Root>
      <CssBaseline />
      <Global
        styles={{
          ".MuiDrawer-root > .MuiPaper-root": {
            height: `calc(50% - ${drawerBleeding}px)`,
            overflow: "visible",
          },
        }}
      />
      <Box sx={{ textAlign: "center", pt: 1 }}>
        <Button onClick={toggleDrawer(true)}>Open</Button>
      </Box>
      <SwipeableDrawer
        container={container}
        anchor="bottom"
        open={open}
        onClose={toggleDrawer(false)}
        onOpen={toggleDrawer(true)}
        swipeAreaWidth={drawerBleeding}
        disableSwipeToOpen={false}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: "none",
          [theme.breakpoints.down("md")]: {
            display: "block",
          },
        }}>
        <DrawerBox>
          <Box display="flex" position="relative">
            <Icon
              iconName={ICON_NAME.MINUS}
              fontSize="large"
              sx={{
                padding: "0",
                position: "absolute",
                left: "50%",
                transform: "translateX(-50%)",
                top: "-7px",
              }}
            />
          </Box>
        </DrawerBox>
        <Box
          sx={{
            px: 2,
            pb: 2,
            height: "100%",
            overflow: "auto",
            background: theme.palette.background.default,
          }}>
          <LayerMobile />
          <LegendMobile />
        </Box>
      </SwipeableDrawer>
    </Root>
  );
};

export default MobileDrawer;
