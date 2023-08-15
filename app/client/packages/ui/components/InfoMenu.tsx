// Copyright (c) 2020 GitHub user u/garronej
import { Menu } from "@mui/material";
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "./../lib/ThemeProvider";

export type InfoMenuProps = {
  className?: string;
  children: React.ReactNode;
  status: boolean;
  handleCloseFunction: VoidFunction;
  menuActions?: React.ReactNode;
  menuHeader?: React.ReactNode;
};

export const InfoMenu = memo(
  forwardRef<HTMLElement, InfoMenuProps>((props, ref) => {
    const {
      className,
      children,
      status,
      menuActions,
      menuHeader,
      handleCloseFunction,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    return (
      <Menu
        open={status}
        anchorEl={ref && "current" in ref ? (ref as React.RefObject<HTMLElement>).current : null}
        id="account-menu"
        onClose={handleCloseFunction}
        onClick={handleCloseFunction}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: "visible",
            filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
            mt: 1.5,
            "& .MuiAvatar-root": {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}>
        <div className={cx(className, classes.menu)}>
          {menuHeader ? <div className={classes.menuHeader}>{menuHeader}</div> : null}

          {children}

          {menuActions ? <div className={classes.menuActions}>{menuActions}</div> : null}
        </div>
      </Menu>
    );
  })
);

const useStyles = makeStyles({ name: { InfoMenu } })((theme) => ({
  menuHeader: {
    marginBottom: "10px",
  },
  menuActions: {
    marginTop: "10px",
    borderTop: `0.4px solid ${theme.colors.useCases.surfaces.background}`,
  },
  menu: {
    padding: "5px 17px",
    minWidth: "270px",
  },
}));
