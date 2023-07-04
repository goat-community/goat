import { Popover } from "@mui/material";
import React, { forwardRef, memo } from "react";

import { makeStyles } from "../lib/ThemeProvider";
import { IconButton, Text } from "./theme";

export type DialogProps = {
  className?: string;
  children?: React.ReactNode;
  title?: string;
  action?: React.ReactNode;
  width: string;
  direction: "center" | "left" | "right";
  onClick: React.MouseEventHandler;
  anchorEl: HTMLButtonElement | null;
};

const Dialog = memo(
  forwardRef<HTMLElement, DialogProps>((props, ref) => {
    const { className, children, title, action, width, direction, onClick, anchorEl, ...rest } = props;
    const { classes, cx } = useStyles({ width });

    return (
      // <Card ref={ref} className={cx(classes.card, className)} width={width} noHover={true}>
      <Popover
        className={classes.popover}
        open={true}
        anchorEl={anchorEl}
        onClose={onClick}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: direction,
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: direction,
        }}>
        <div className={cx(classes.card, className)}>
          {title ? (
            <div className={classes.header}>
              {/* header */}
              <Text typo="navigation label">{title}</Text>
              <span onClick={onClick}>
                <IconButton className={classes.xButton} type="submit" size="small" iconId="close" />
              </span>
            </div>
          ) : null}
          <div>
            {/* header */}
            {children}
          </div>

          {action ? (
            <div className={classes.footer}>
              {/* action */}
              {action}
            </div>
          ) : null}
        </div>
      </Popover>
      // </Card>
    );
  })
);

const useStyles = makeStyles<{ width: string }>({
  name: { Dialog },
})((theme, { width }) => ({
  card: {
    backgroundColor: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].light,
    maxHeight: "500px",
    padding: `${theme.spacing(3)}px ${theme.spacing(5)}px`,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: theme.spacing(3),
  },
  footer: {
    marginTop: theme.spacing(3),
  },
  xButton: {
    position: "absolute",
    right: theme.spacing(3),
    top: "8px",
  },
  popover: {
    ".MuiPopover-paper": {
      width: width,
    },
  },
}));

export default Dialog;
