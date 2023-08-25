"use client";

import { makeStyles } from "@/lib/theme";
import { List, ListItem, ListItemButton, ListItemIcon } from "@mui/material";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { v4 } from "uuid";
import { Text, useTheme } from "@p4b/ui/components/theme";
import { Icon } from "@p4b/ui/components/Icon";
import type { ICON_NAME } from "@p4b/ui/components/Icon";

export type DashboardSidebarProps = {
  items: { link: string; icon: ICON_NAME; placeholder: string }[];
  width: number;
  extended_width: number;
  children: React.ReactNode;
  lng: string;
};

/**
 * A functional component that renders a dashboard sidebar.
 * @param {DashboardSidebarProps} props - The props object containing the items and children.
 * @returns The rendered dashboard sidebar component.
 */

export function DashboardSidebar(props: DashboardSidebarProps) {
  const { items, children, lng } = props;

  const pathname = usePathname();

  // styling
  const { classes, cx } = useStyles(props)();
  const theme = useTheme();

  // Component States
  const [hover, setHover] = useState(false);
  const [_, setActive] = useState<string | null>(items[0].placeholder);

  function activeColor(path) {
    if (pathname.includes(`/${lng}${path}`)) {
      return theme.colors.palette.focus.main;
    } else {
      return theme.colors.palette.light.greyVariant4;
    }
  }

  return (
    <>
      <nav
        className={cx(classes.root)}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}>
        <List>
          {items?.map(({ link, icon, placeholder }) => (
            <Link href={`${link}`} className={classes.textName} key={v4()}>
              <ListItem onClick={() => setActive(placeholder)} disablePadding>
                <ListItemButton className={classes.itemList}>
                  <ListItemIcon>
                    <Icon iconName={icon} htmlColor={activeColor(link)} fontSize="small" />
                  </ListItemIcon>
                  {hover ? (
                    <Text
                      typo="body 2"
                      className={classes.textName}
                      color={pathname.includes(`/${lng}${link}`) ? "focus" : "primary"}>
                      {placeholder}
                    </Text>
                  ) : null}
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

const useStyles = (props: DashboardSidebarProps) =>
  makeStyles({ name: { DashboardSidebar } })((theme) => ({
    root: {
      zIndex: "20",
      paddingTop: "52px",
      backgroundColor: theme.colors.useCases.surfaces.background,
      cursor: "pointer",
      width: props.width,
      left: 0,
      top: 0,
      bottom: 0,
      position: "fixed",
      transition: "width 0.4s ease",
      display: "flex",
      overflow: "hidden",
      flexDirection: "column",
      boxShadow: "0px 1px 5px 0px #0000001F, 0px 2px 2px 0px #00000024, 0px 3px 1px -2px #00000033",
      "&:hover": {
        width: props.extended_width,
      },
    },
    itemList: {
      "&:hover": {
        backgroundColor: `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant2}aa`,
      },
    },
    textName: {
      textDecoration: "none",
    },
  }));
