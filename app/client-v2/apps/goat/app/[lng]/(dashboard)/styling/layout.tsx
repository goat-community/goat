"use client";

import StylingSideBar from "@/app/[lng]/(dashboard)/styling/StylingSideBar";
import { makeStyles } from "@/lib/theme";

interface StylingLayoutProps {
  children: React.ReactNode;
}

const StylingLayout = (props: StylingLayoutProps) => {
  const { children } = props;
  const { classes } = useStyles();

  return <StylingSideBar width={48}>{children}</StylingSideBar>;
};

const useStyles = makeStyles({ name: { StylingLayout } })(() => ({}));

export default StylingLayout;
