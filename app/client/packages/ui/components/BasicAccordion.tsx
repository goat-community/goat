"use client";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

import { makeStyles } from "../lib/ThemeProvider";

export type BasicAccordionTypes = {
  className?: string;
  title: string;
  children: NonNullable<ReactNode>;
  variant?: "primary" | "secondary";
};

const useStyles = () =>
  makeStyles({ name: { BasicAccordion } })(() => ({
    root: {},
    primary: {},
    secondary: {
      "& .MuiPaper-root": {
        boxShadow: "unset",
        background: "transparent",
      },
    },
    content: {
      padding: "0 16px",
    },
  }));

export default function BasicAccordion(props: BasicAccordionTypes) {
  const { children, title, variant = "primary" } = props;

  const { classes, cx } = useStyles()();
  const expandIconColor = variant === "secondary" ? "secondary" : "inherit";
  return (
    <div className={cx(classes.root, variant && classes[variant])}>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon color={expandIconColor} />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          className={cx(classes.content)}
        >
          <Typography>{title}</Typography>
        </AccordionSummary>
        <AccordionDetails className={cx(classes.content)}>
          {children}
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
