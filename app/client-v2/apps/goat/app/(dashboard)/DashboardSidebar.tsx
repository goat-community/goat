"use client";

import { makeStyles } from "@/lib/theme";
import { Text } from "@/lib/theme";
import { useTheme } from "@/lib/theme";
import { Fade, List, ListItem, ListItemButton, ListItemIcon } from "@mui/material";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Icon } from "@p4b/ui/components/theme";
import type { IconId } from "@p4b/ui/components/theme";

export type DashboardSidebarProps = {
  items: { link: string; icon: IconId; placeholder: string }[];
  width: number;
  extended_width: number;
  children: React.ReactNode;
};

export function DashboardSidebar(props: DashboardSidebarProps) {
  const { items, children } = props;
  const router = useRouter();
  const { classes, cx } = useStyles(props)();
  const theme = useTheme();
  const [hover, setHover] = useState(false);
  const pathname = usePathname();
  const handleHover = () => {
    setHover((currHover) => !currHover);
  };
  return (
    <>
      <nav className={cx(classes.root)} onMouseEnter={handleHover} onMouseLeave={handleHover}>
        <List>
          {items?.map(({ link, icon, placeholder }, indx) => (
            <ListItem onClick={() => router.push(link)} disablePadding key={indx}>
              <ListItemButton className={classes.itemList}>
                <ListItemIcon sx={{ marginRight: "10px" }}>
                  <Icon
                    size="default"
                    iconId={icon}
                    iconVariant={
                      pathname.includes(link) ? "focus" : theme.isDarkModeEnabled ? "white" : "gray"
                    }
                  />
                </ListItemIcon>
                {hover ? (
                  <Fade in={true}>
                    <Text typo="body 2" color={pathname.startsWith(link) ? "focus" : "primary"}>
                      {placeholder}
                    </Text>
                  </Fade>
                ) : (
                  <></>
                )}
              </ListItemButton>
            </ListItem>
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
      backgroundColor: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].light,
      cursor: "pointer",
      width: props.width,
      left: 0,
      top: 0,
      bottom: 0,
      position: "fixed",
      transition: "width 0.4s ease",
      display: "flex",
      flexDirection: "column",
      boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
      "&:hover": {
        width: props.extended_width,
      },
    },
    itemList: {
      "&:hover": {
        backgroundColor: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1,
      },
    },
  }));
