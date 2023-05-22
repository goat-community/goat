import FolderIcon from "@mui/icons-material/Folder";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import { Fade, Link, Stack, Typography } from "@mui/material";
import Box from "@mui/material/Box";

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
  extended: boolean;
  items: { link: string; iconId: "home" | "help" | "folder" | "settings"; placeholder: string }[];
};

export function Sidebar(props: SidebarProps) {
  const { extended, items } = props;
  const { classes, cx } = useStyles();

  return (
    <Box className={cx(classes.root, { [classes.extended]: extended })}>
      {items?.map(({ link, iconId, placeholder }) => (
        <Box key={link} className={cx(classes.item, { [classes.extended_item]: extended })}>
          <Link href={link}>
            {extended ? (
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

const useStyles = makeStyles({ name: { Sidebar } })((theme) => ({
  root: {
    backgroundColor: theme.colors.palette.light.light,
    width: SIDEBAR_WIDTH,
    left: 0,
    top: 0,
    bottom: 0,
    position: "fixed",
    transition: "width 0.4s ease",
    display: "flex",
    flexDirection: "column",
  },
  extended: {
    width: SIDEBAR_WIDTH_EXTENDED,
  },
  item: {
    height: 48,
    marginBottom: 4,
    width: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  extended_item: {
    justifyContent: "flex-start",
    padding: "0 15px",
  },
}));
