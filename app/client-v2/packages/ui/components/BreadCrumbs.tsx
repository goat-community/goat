'use client'

import * as React from 'react';
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
        <Link
          underline="hover"
          href="/"
        >
          Home
        </Link>
        <Link
          underline="hover"
          href="/"
        >
          Folder XYZ
        </Link>
        <Link
          underline="hover"
          href="/"
        >
          Link
        </Link>
      </Breadcrumbs>
    </div>
  );
}
