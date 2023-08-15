import React, { forwardRef, memo } from "react";

import { Card } from ".";
import { GOATLogoGreenSvg } from "../../assets/svg/GOATLogoGreen";
import { makeStyles } from "../../lib/ThemeProvider";

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
    const { className, imageSide = "right", content, image, actions} = props;

    const { classes, cx } = useStyles({
      imageSide,
      image,
    });

    return (
      <Card className={cx(classes.card, className)} width="100%" noHover={true}>
        <div className={classes.bannerCard}>
          {imageSide !== "full" ? (
            <>
              <div className={classes.container}>
                <div>{content}</div>
                <div>{actions}</div>
              </div>
              {imageSide === "fullBehind" ? (
                <div />
              ) : (
                <div className={classes.image}>
                  <span
                    style={{
                      position: "absolute",
                      width: "100%",
                      height: "100%",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}>
                    <GOATLogoGreenSvg height={100} width={200} />
                  </span>
                  <div />
                </div>
              )}
            </>
          ) : (
            <div />
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
    backgroundColor: theme.colors.palette.dark.main,
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
      borderRadius: 4,
      left: "0",
      top: "0",
      width: "100%",
      height: "100%",
      background:
        "radial-gradient(50% 50% at 50% 50%, rgba(40,54,72,0.8) 0%, rgba(40,54,72,0.9) 100%), url(https://assets.plan4better.de/img/login/artwork_1.png) no-repeat center",
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
  // overlay: {
  //   position: "absolute",
  //   top: "0",
  //   left: "0",
  //   width: "100%",
  //   height: "100%",
  //   backgroundColor: "rgba(40, 54, 72, 0.8)",
  // },
}));

export default Banner;
