"use client";

import { makeStyles } from "@/lib/theme";
import { List, ListItem, ListItemButton, ListItemIcon } from "@mui/material";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { v4 } from "uuid";

import type { IconId } from "@p4b/ui/components/theme";
import { Icon, useTheme } from "@p4b/ui/components/theme";

export type IStylingSideBarProps = {
  width: number;
  children: React.ReactNode;
};

const items: { link: string; icon: IconId; value: string }[] = [
  {
    link: "/home",
    icon: "home",
    value: "Home",
  },
  {
    link: "/content",
    icon: "folder",
    value: "Content",
  },
  {
    link: "/settings",
    icon: "settings",
    value: "Settings",
  },
  {
    link: "/styling",
    icon: "colorLens",
    value: "Styling",
  },
  {
    link: "/help",
    icon: "help",
    value: "Help",
  },
];

function StylingSideBar(props: IStylingSideBarProps) {
  const { children } = props;

  const pathname = usePathname();

  // styling
  const { classes, cx } = useStyles(props)();
  const theme = useTheme();

  // Component States
  const [hover, setHover] = useState(false);
  const [active, setActive] = useState<string | null>(items[0].value);

  return (
    <>
      <nav
        className={cx(classes.root)}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}>
        <List>
          {items?.map(({ link, icon, value }) => (
            <Link href={`${link}`} className={classes.textName} key={v4()}>
              <ListItem onClick={() => setActive(value)} disablePadding>
                <ListItemButton className={classes.itemList}>
                  <ListItemIcon>
                    <Icon
                      size="default"
                      iconId={icon}
                      iconVariant={pathname === link ? "focus" : theme.isDarkModeEnabled ? "white" : "gray"}
                    />
                  </ListItemIcon>
                </ListItemButton>
              </ListItem>
            </Link>
          ))}
        </List>
      </nav>
      {children}
    </>
  );
}

const useStyles = (props: IStylingSideBarProps) =>
  makeStyles({ name: { StylingSideBar } })((theme) => ({
    root: {
      zIndex: "20",
      paddingTop: "52px",
      backgroundColor: theme.colors.useCases.surfaces.surface2,
      cursor: "pointer",
      width: props.width,
      right: 0,
      top: 0,
      bottom: 0,
      position: "fixed",
      transition: "width 0.4s ease",
      display: "flex",
      overflow: "hidden",
      flexDirection: "column",
      boxShadow: "0px 1px 5px 0px #0000001F, 0px 2px 2px 0px #00000024, 0px 3px 1px -2px #00000033",
    },
    itemList: {
      "&:hover": {
        backgroundColor: `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant2}aa`,
      },
    },
  }));

export default StylingSideBar;
