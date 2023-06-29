import { Link, Stack } from "@mui/material";

import { GOATLogoGreenSvg } from "../assets/svg/GOATLogoGreen";
import { makeStyles } from "../lib/ThemeProvider";
import { TextField } from "./Text/TextField";

export type ToolbarProps = {
  items: { link: string; icon: () => JSX.Element }[];
  height: number;
};

export function Toolbar(props: ToolbarProps) {
  const { items } = props;
  const { classes, cx } = useStyles(props)();

  return (
    <Stack className={cx(classes.root)} direction="row" justifyContent="space-between" alignItems="center">
      <GOATLogoGreenSvg className={classes.logoSize} />
      <TextField
        size="small"
        iconId="search"
        placeholder="Search..."
        className={classes.searchInput}
        filled={true}
        sx={{ paddingY: "6px" }}
      />
      <Stack direction="row" alignItems="center" sx={{ paddingY: "6px" }}>
        {items?.map(({ link, icon }, index) => (
          <Link
            className={index !== items.length - 1 ? classes.icon : classes.lastIcon}
            href={link}
            key={index}>
            {icon()}
          </Link>
        ))}
      </Stack>
    </Stack>
  );
}

const useStyles = (props: ToolbarProps) =>
  makeStyles({ name: { Toolbar } })((theme) => ({
    root: {
      position: "fixed",
      backgroundColor: theme.muiTheme.palette.background.paper,
      height: props.height,
      top: 0,
      left: 0,
      right: 0,
      padding: theme.spacing(4),
      zIndex: "100",
      boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
    },
    logoSize: {
      width: "144px",
      height: "36px",
    },
    searchInput: {
      width: "440px",
      border: "none",
    },
    icon: {
      borderRight: `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].light}14`,
      padding: "4px",
      paddingRight: theme.spacing(3),
      marginRight: theme.spacing(3),
    },
    lastIcon: {
      padding: "4px",
      marginLeft: "0px",
      "& .css-111rfow-MuiStack-root>:not(style)+:not(style)": {
        marginLeft: "0px",
      },
    },
  }));
