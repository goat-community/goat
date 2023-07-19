'use client'

import * as React from 'react';
import Typography from '@mui/material/Typography';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';

export type BreadcrumbsType = {
  items?: object[];
  className?: string;
  eventHandler: any;
}

export default function BasicBreadcrumbs(props: BreadcrumbsType) {

  const {
    className,
    items,
    eventHandler
  } = props;

  return (
    <div role="presentation" onClick={eventHandler}>
      <Breadcrumbs aria-label="breadcrumb">
        <Link underline="hover" color="inherit" href="/">
          MUI
        </Link>
        <Link
          underline="hover"
          color="inherit"
          href="/"
        >
          Core
        </Link>
        <Typography color="text.primary">Breadcrumbs</Typography>
      </Breadcrumbs>
    </div>
  );
}
