"use client";

import { makeStyles } from "@/lib/theme";
import { Fade, List, ListItem, ListItemButton, ListItemIcon } from "@mui/material";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Icon, Text, useTheme } from "@p4b/ui/components/theme";
import type { IconId } from "@p4b/ui/components/theme";

export type DashboardSidebarProps = {
  items: { link: string; icon: IconId; placeholder: string }[];
  width: number;
  extended_width: number;
  children: React.ReactNode;
};

/**
 * A functional component that renders a dashboard sidebar.
 * @param {DashboardSidebarProps} props - The props object containing the items and children.
 * @returns The rendered dashboard sidebar component.
 */

export function DashboardSidebar(props: DashboardSidebarProps) {
  const { items, children } = props;
  const router = useRouter();

  const pathname = usePathname();

  // styling
  const { classes, cx } = useStyles(props)();
  const theme = useTheme();

  // Component States
  const [hover, setHover] = useState(false);
  const [active, setActive] = useState<string | null>(items[0].placeholder);

  // functions
  const handleHover = () => {
    setHover((currHover) => !currHover);
  };

  const handleChangeLink = (link, placeholder) => {
    setActive(placeholder);
    router.push(link);
  };

  return (
    <>
      <nav className={cx(classes.root)} onMouseEnter={handleHover} onMouseLeave={handleHover}>
        <List>
          {items?.map(({ link, icon, placeholder }, indx) => (
            <Link href={link} className={classes.textName} key={link}>
              <ListItem onClick={() => setActive(placeholder)} disablePadding key={indx}>
                <ListItemButton className={classes.itemList}>
                  <ListItemIcon>
                    <Icon
                      size="default"
                      iconId={icon}
                      iconVariant={pathname === link ? "focus" : theme.isDarkModeEnabled ? "white" : "gray"}
                    />
                  </ListItemIcon>
                  {hover ? (
                    <Fade in={true}>
                      <Text
                        typo="body 2"
                        className={classes.textName}
                        color={pathname === link ? "focus" : "primary"}>
                        {placeholder}
                      </Text>
                    </Fade>
                  ) : (
                    <></>
                  )}
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
      backgroundColor: theme.colors.useCases.surfaces.surface2,
      cursor: "pointer",
      width: props.width,
      left: 0,
      top: 0,
      bottom: 0,
      position: "fixed",
      transition: "width 0.4s ease",
      display: "flex",
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
