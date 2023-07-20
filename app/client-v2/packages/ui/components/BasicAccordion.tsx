'use client';

import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { ReactNode } from "react";
import { makeStyles } from "../lib/ThemeProvider";

export type BasicAccordionTypes = {
  className?: string;
  title: string;
  children: NonNullable<ReactNode>;
};


const useStyles = () =>
  makeStyles({ name: { BasicAccordion } })(() => ({
    root: {},
    content: {
      padding: '0 16px'
    }
  }));

export default function BasicAccordion(props: BasicAccordionTypes) {

  const { children, title } = props

  const { classes, cx } = useStyles()();


  return (
    <div className={cx(classes.root)}>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          className={cx(classes.content)}
        >
          <Typography>{ title }</Typography>
        </AccordionSummary>
        <AccordionDetails className={cx(classes.content)}>
          {children}
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
