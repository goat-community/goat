import { Box, useTheme } from "@mui/material";
import React, { useEffect, useRef } from "react";

interface CustomMenuProps {
  children: React.ReactNode;
  close: () => void;
}

const CustomMenu = (props: CustomMenuProps) => {
  const { children, close } = props;

  const menu = useRef<HTMLDivElement | null>(null);

  const theme = useTheme();

  useEffect(() => {
    document.addEventListener("click", handleClickOutside, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleClickOutside(e: Event) {
    if (menu.current && !menu.current.contains(e.target as Node)) {
      close();
    }
  }

  return (
    <Box
      component="div"
      sx={{
        position: "absolute",
        top: "80%",
        right: "5px",
        background: theme.palette.background.paper,
        borderRadius: theme.spacing(2),
        zIndex: "20",
      }}
      ref={menu}>
      {children}
    </Box>
  );
};

export default CustomMenu;
