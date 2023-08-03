"use client";

import React from "react";
import { v4 } from "uuid";

import { useTranslation } from "../../../../apps/goat/app/i18/client";
import { makeStyles } from "../../lib/ThemeProvider";
import P4BLogo from "../P4BLogo";
import { Text, Icon } from "../theme";

export type FooterProps = {
  className?: string;
  lng: string;
};

const Footer = (props: FooterProps) => {
  const { className, lng } = props;

  const { classes, cx } = useStyles();

  const { t } = useTranslation(lng, "footer");

  const links = [
    {
      header: t("navigate"),
      links: [
        {
          name: "Home it work",
        },
        {
          name: "Pricing",
        },
        {
          name: "Blog",
        },
        {
          name: "Demo",
        },
      ],
    },
    {
      header: t("study_areas"),
      links: [
        {
          name: "Germany",
        },
        {
          name: "EU",
        },
        {
          name: "UK",
        },
        {
          name: "Asia",
        },
        {
          name: "Americas",
        },
      ],
    },
    {
      header: t("contact"),
      links: [
        {
          icon: "phone",
          name: "+49 89 2000 708 30",
          underline: true,
        },
        {
          icon: "email",
          name: "info@plan4better.de",
          underline: true,
        },
        {
          icon: "marker",
          name: "Am Kartoffelgarten 14 c/o WERK1 81671 München Germany",
          underline: true,
        },
      ],
    },
  ];

  return (
    <div className={cx(classes.root, className)}>
      <div className={classes.info}>
        <P4BLogo width={100} />
        <Text typo="caption" className={classes.footerText}>
          {t("info")}
        </Text>
        <div className={classes.dots}>
          <div className={classes.dot} />
          <div className={classes.dot} />
          <div className={classes.dot} />
          <div className={classes.dot} />
        </div>
      </div>
      <div className={classes.links}>
        {links.map((link) => (
          <div key={v4()}>
            <Text typo="body 3" className={classes.headLinks}>
              {link.header}
            </Text>
            {link.links.map((itemLink) => (
              <Text
                typo="caption"
                key={v4()}
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
};

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
