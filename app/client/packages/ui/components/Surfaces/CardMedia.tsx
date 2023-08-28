// Copyright (c) 2020 GitHub user u/garronej
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";

export type CardMediaProps = {
  src: string;
  alt?: string;
  className?: string;
};

export const CardMedia = memo(
  forwardRef<HTMLElement, CardMediaProps>((props) => {
    const {
      src,
      alt,
      className,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    return (
      <>
        <img src={src} alt={alt} className={cx(classes.media, className)} />
      </>
    );
  })
);

const useStyles = makeStyles({ name: { CardMedia } })(() => ({
  media: {
    width: "100%",
    height: "100px",
    borderTopRightRadius: 4,
    borderTopLeftRadius: 4,
    objectFit: "cover",
  },
}));
