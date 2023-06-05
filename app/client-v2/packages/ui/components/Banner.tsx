import React, { forwardRef, memo } from "react";

import { makeStyles } from "../lib/ThemeProvider";
import { Card } from "./Card";

export type BannerProps = {
  className?: string;
  children?: React.ReactNode;
  imageSide?: "left" | "right" | "full" | "fullBehind";
  content?: React.ReactNode;
  image?: string;
  actions?: React.ReactNode;
};

const Banner = memo(
  forwardRef<any, BannerProps>((props) => {
    const {
      className,
      children,
      imageSide = "right",
      content,
      image,
      actions,

      ...rest
    } = props;

    const { classes, cx } = useStyles({
      imageSide,
      image,
    });

    return (
      <Card className={classes.card} width="100%" noHover={true}>
        {" "}
        {/* Hug (210px) */}
        <div className={classes.bannerCard}>
          {imageSide !== "full" ? (
            <>
              <div className={classes.container}>
                <div>{content}</div>
                <div>{actions}</div>
              </div>
              {imageSide === "fullBehind" ? (
                <div className={classes.overlay} />
              ) : (
                <div className={classes.image}>
                  <div className={classes.overlay} />
                </div>
              )}
            </>
          ) : (
            <div className={classes.overlay} />
          )}
        </div>
      </Card>
    );
  })
);

const imageWidthBasedOnImageSide = (side: "left" | "right" | "full" | "fullBehind") => {
  switch (side) {
    case "left":
    case "right":
      return "31%";
    case "full":
    case "fullBehind":
      return "100%";
  }
};

const useStyles = makeStyles<{
  imageSide?: "left" | "right" | "full" | "fullBehind";
  image?: string;
}>({
  name: { Banner },
})((theme, { imageSide, image }) => ({
  card: {
    backgroundColor: theme.colors.palette.dark.light,
    position: "relative",
  },
  bannerCard: {
    height: "210px",
    display: "flex",
    backgroundImage: image && imageSide && !["right", "left"].includes(imageSide) ? `url("${image}")` : "",
    flexDirection: imageSide === "left" ? "row-reverse" : "row",
  },
  image: {
    width: image && imageSide ? imageWidthBasedOnImageSide(imageSide) : "0",
    position: "relative",
    "&::before": {
      content: '""',
      position: "absolute",
      left: "0",
      top: "0",
      width: "100%",
      height: "100%",
      backgroundImage:
        image && imageSide && !["full", "fullBehind"].includes(imageSide) ? `url("${image}")` : "",
      "-webkit-filter": "grayscale(90%)" /* Safari 6.0 - 9.0 */,
      filter: "grayscale(90%)",
      backgroundPosition: "7% 30%",
    },
  },
  container: {
    padding: theme.spacing(5),
    width: image && imageSide && !["full", "fullBehind"].includes(imageSide) ? "69%" : "0",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    color: "white",
    zIndex: "100",
  },
  overlay: {
    position: "absolute",
    top: "0",
    left: "0",
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(40, 54, 72, 0.8)",
  },
}));

export default Banner;
