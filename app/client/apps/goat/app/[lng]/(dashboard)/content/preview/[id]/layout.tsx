"use client";

import { makeStyles } from "@/lib/theme";

import Box from "@p4b/ui/components/Box";

interface ContentLayoutProps {
  children: React.ReactNode;
}

const ContentLayout = (props: ContentLayoutProps) => {
  const { children } = props;

  const { classes } = useStyles();

  return <Box className={classes.root}>{children}</Box>;
};

const useStyles = makeStyles({ name: { ContentLayout } })(() => ({
  root: {
    margin: "0 auto",
    maxWidth: "1168px",
    width: "100%",
  },
}));

export default ContentLayout;
