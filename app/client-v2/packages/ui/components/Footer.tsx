"use client";

import React, { forwardRef, memo } from "react";

import { makeStyles } from "../lib/ThemeProvider";
import P4BLogo from "./P4BLogo";
import { Text, Icon } from "./theme";
import type { IconId } from "./theme";

export type FooterProps = {
  className?: string;
  children?: React.ReactNode;
  links: { header: string; links: { name: string; underline?: boolean; icon?: IconId }[] }[];
  text: string;
};

const Footer = memo(
  forwardRef<any, FooterProps>((props, ref) => {
    const { className, children, links, text } = props;

    const { classes, cx } = useStyles();

    return (
      <div className={classes.root}>
        <div className={classes.info}>
          <P4BLogo width={100} />
          <Text typo="caption" className={classes.footerText}>
            {text}
          </Text>
          <div className={classes.dots}>
            <div className={classes.dot} />
            <div className={classes.dot} />
            <div className={classes.dot} />
            <div className={classes.dot} />
          </div>
        </div>
        <div className={classes.links}>
          {links.map((link, index) => (
            <div key={index}>
              <Text typo="body 3" className={classes.headLinks}>
                {link.header}
              </Text>
              {link.links.map((itemLink, indx) => (
                <Text
                  typo="caption"
                  key={indx}
                  className={cx(classes.linkItem, itemLink.underline ? classes.underline : "")}>
                  {itemLink.icon ? <Icon size="small" iconVariant="white" iconId={itemLink.icon} /> : null}{" "}
                  {itemLink.name}
                </Text>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  })
);

const useStyles = makeStyles({
  name: { Footer },
})((theme) => ({
  root: {
    zIndex: "1000",
    width: "100%",
    padding: "48px 96px",
    marginTop: "100px",
    position: "relative",
    display: "flex",
    "@media (max-width: 650px)": {
      flexDirection: "column",
      gap: theme.spacing(5),
      padding: "40px 40px",
    },
    justifyContent: "space-between",
    backgroundColor: theme.colors.palette.dark.main,
  },
  dots: {
    display: "flex",
    gap: theme.spacing(2),
  },
  dot: {
    width: theme.spacing(3),
    height: theme.spacing(3),
    borderRadius: "50%",
    backgroundColor: theme.colors.palette.focus.main,
  },
  footerText: {
    color: theme.colors.palette.light.greyVariant1,
    margin: "21px 0",
    "@media (max-width: 450px)": {
      fontSize: "10px",
    },
  },
  info: {
    width: "30%",
    position: "relative",
    "@media (max-width: 650px)": {
      width: "100%",
    },
  },
  links: {
    width: "35%",
    display: "flex",
    justifyContent: "space-between",
    gap: theme.spacing(2),
    "@media (max-width: 1500px)": {
      width: "45%",
    },
    "@media (max-width: 991px)": {
      width: "55%",
    },
    "@media (max-width: 650px)": {
      width: "100%",
    },
    "@media (max-width: 450px)": {
      flexDirection: "column",
      gap: theme.spacing(5),
    },
  },
  headLinks: {
    fontWeight: "bold",
    color: theme.colors.palette.light.main,
    "@media (max-width: 450px)": {
      fontSize: "12px",
    },
  },
  linkItem: {
    color: theme.colors.palette.light.greyVariant1,
    display: "flex",
    gap: theme.spacing(1),
    paddingTop: "9px",
    maxWidth: "220px",
    "@media (max-width: 991px)": {
      maxWidth: "160px",
    },
    "@media (max-width: 450px)": {
      fontSize: "12px",
    },
  },
  underline: {
    textDecoration: "underline",
    paddingTop: "20px",
  },
}));

// "@media (max-width: 1714px)": {
//   width: "90%",
// },
// "@media (max-width: 1500px)": {
//   width: "90%",
// },
// "@media (max-width: 991px)": {
//   paddingLeft: "50px",
// },

export default Footer;