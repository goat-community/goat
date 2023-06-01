import { Fade, Link, Stack, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { useState } from "react";

import { makeStyles } from "../lib/ThemeProvider";

export type DashboardSidebarProps = {
  items: { link: string; icon: () => JSX.Element; placeholder: string }[];
  width: number;
  extended_width: number;
};

export function DashboardSidebar(props: DashboardSidebarProps) {
  const { items } = props;
  const { classes, cx } = useStyles(props)();

  const [hover, setHover] = useState(false);

  const handleHover = () => {
    setHover((currHover) => !currHover);
  };

  return (
    <Box className={cx(classes.root)} onMouseEnter={handleHover} onMouseLeave={handleHover}>
      {items?.map(({ link, icon, placeholder }) => (
        <Box key={link} className={cx(classes.item, { [classes.itemHover]: hover })}>
          <Link href={link}>
            {hover ? (
              <Fade in={true}>
                <Stack direction="row" spacing="14px" alignItems="center">
                  {icon()}
                  <Typography fontSize="14px" color="#103361">
                    {placeholder}
                  </Typography>
                </Stack>
              </Fade>
            ) : (
              <>{icon()}</>
            )}
          </Link>
        </Box>
      ))}
    </Box>
  );
}

const useStyles = (props: DashboardSidebarProps) =>
  makeStyles({ name: { DashboardSidebar } })((theme) => ({
    root: {
      backgroundColor: theme.colors.palette.light.light,
      cursor: "pointer",
      width: props.width,
      left: 0,
      top: 0,
      bottom: 0,
      position: "fixed",
      transition: "width 0.4s ease",
      display: "flex",
      flexDirection: "column",
      "&:hover": {
        width: props.extended_width,
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
