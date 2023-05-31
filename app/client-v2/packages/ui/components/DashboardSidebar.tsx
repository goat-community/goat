import FolderIcon from "@mui/icons-material/Folder";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import { Fade, Link, Stack, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { useState } from "react";

import { SIDEBAR_WIDTH, SIDEBAR_WIDTH_EXTENDED } from "../constants/sidebar";
import { makeStyles } from "../lib/ThemeProvider";
import { createIcon } from "./Icon";

const { Icon } = createIcon({
  help: HelpIcon,
  home: HomeIcon,
  settings: SettingsSuggestIcon,
  folder: FolderIcon,
});

export type SidebarProps = {
  items: { link: string; iconId: "home" | "help" | "folder" | "settings"; placeholder: string }[];
};

export function DashboardSidebar(props: SidebarProps) {
  const { items } = props;
  const { classes, cx } = useStyles();

  const [hover, setHover] = useState(false);

  const handleHover = () => {
    setTimeout(() => {
      setHover((currHover) => !currHover);
    }, 100);
  };

  return (
    <Box className={cx(classes.root)} onMouseEnter={handleHover} onMouseLeave={handleHover}>
      {items?.map(({ link, iconId, placeholder }) => (
        <Box key={link} className={cx(classes.item, { [classes.itemHover]: hover })}>
          <Link href={link}>
            {hover ? (
              <Fade in={true}>
                <Stack direction="row" spacing="14px" alignItems="center">
                  <Icon iconId={iconId} />
                  <Typography fontSize="14px" color="#103361">
                    {placeholder}
                  </Typography>
                </Stack>
              </Fade>
            ) : (
              <Icon iconId={iconId} size="large" />
            )}
          </Link>
        </Box>
      ))}
    </Box>
  );
}

const useStyles = makeStyles({ name: { DashboardSidebar } })((theme) => ({
  root: {
    backgroundColor: theme.colors.palette.light.light,
    cursor: "pointer",
    width: SIDEBAR_WIDTH,
    left: 0,
    top: 0,
    bottom: 0,
    position: "fixed",
    transition: "width 0.4s ease",
    display: "flex",
    flexDirection: "column",
    "&:hover": {
      width: SIDEBAR_WIDTH_EXTENDED,
    },
  },
  item: {
    height: 48,
    marginBottom: 4,
    width: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  itemHover: {
    justifyContent: "flex-start",
    padding: "0 15px",
  },
}));
