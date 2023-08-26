import { makeStyles } from "@/lib/theme";
import React from "react";
import { Icon } from "@p4b/ui/components/Icon";
import type {ICON_NAME} from "@p4b/ui/components/Icon";

interface WrappedIcon {
  icon: ICON_NAME
}

const WrappedIcon = (props: WrappedIcon) => {

  const {icon} = props;

  const {classes} = useStyles();

  return (
    <div className={classes.wrapped}>
      <Icon iconName={icon} />
    </div>
  );
};

const useStyles = makeStyles({ name: { WrappedIcon } })((theme) => ({
  wrapped: {
    padding: "5px",
    display: "flex",
    background: `${theme.colors.palette.focus.main}14`,
    borderRadius: "50%",
  }
}));


export default WrappedIcon;
