/* eslint-disable react/display-name */
import { Avatar as MUIAvatar } from "@mui/material";
import { memo } from "react";
import { makeStyles } from "@/lib/theme";
import { Text } from "@/lib/theme";

export type AvatarProps = {
  className?: string;
  size?: number;
  label?: string;
  image?: string;
  color?: "primary" | "focus" | "error" | "warning" | "success" | "info" | "default";
};

export const Avatar = memo((props: AvatarProps) => {
  const { className, size = 40, color = "default", label, image } = props;

  const { classes, cx } = useStyles({ color, size });

  return (
    <MUIAvatar
      className={cx(className, classes.avatar)}
      sx={{ width: size, height: size }}
      src={image ? image : undefined}>
      <Text typo="caption" className={classes.teamTitle}>
        {label}
      </Text>
    </MUIAvatar>
  );
});

const useStyles = makeStyles<{ color: string; size: number }>({
  name: { Avatar },
})((theme, { color, size }) => {
  let backColor = "";

  switch (color) {
    case "primary":
      backColor = theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].main;
      break;
    case "focus":
      backColor = theme.colors.palette.focus.main;
      break;
    case "error":
      backColor = theme.colors.palette.redError.main;
      break;
    case "warning":
      backColor = theme.colors.palette.orangeWarning.main;
      break;
    case "success":
      backColor = theme.colors.palette.greenSuccess.main;
      break;
    case "info":
      backColor = theme.colors.palette.blueInfo.main;
      break;
    default:
      break;
  }

  let fontsize = "13px";

  switch (true) {
    case size < 30:
      break;
    case size < 40:
      fontsize = "16px";
      break;
    case size > 40:
      fontsize = "18px";
      break;
  }

  return {
    avatar: {
      backgroundColor: backColor ? backColor : undefined,
      fontSize: fontsize,
    },
    teamTitle: {
      color: theme.colors.palette.light.main,
    },
  };
});
