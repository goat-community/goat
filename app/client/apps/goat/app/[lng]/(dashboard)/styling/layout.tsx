"use client";

import StylingSideBar from "@/components/styling/StylingSideBar";
import React from "react";

interface StylingLayoutProps {
  children: React.ReactNode;
}

const StylingLayout = (props: StylingLayoutProps) => {
  const { children } = props;
  // const { classes } = useStyles();

  return (
    <StylingSideBar width={48} extended_width={268}>
      {children}
    </StylingSideBar>
  );
};

// const useStyles = makeStyles({ name: { StylingLayout } })(() => ({}));

export default StylingLayout;
