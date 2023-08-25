// Copyright (c) 2020 GitHub user u/garronej
import Box from "@mui/material/Box";
import MobileStepper from "@mui/material/MobileStepper";
import { forwardRef, memo } from "react";
import React from "react";
import SwipeableViews from "react-swipeable-views";
import { autoPlay } from "react-swipeable-views-utils";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "./../lib/ThemeProvider";
import { Text } from "./theme";

const AutoPlaySwipeableViews = autoPlay(SwipeableViews);

export type SlideShowProps = {
  className?: string;
  images: {
    label?: string;
    imgPath: string;
    description?: string;
  }[];
  children?: React.ReactNode;
  height: number;
  width: string;
};

export const SlideShow = memo(
  forwardRef<HTMLElement, SlideShowProps>((props) => {
    const {
      className,
      images,
      children,
      height,
      width,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    // Styling related
    const { classes } = useStyles();
    // Component States
    const [activeStep, setActiveStep] = React.useState(0);

    const maxSteps = images.length;

    // Functions
    const handleStepChange = (step: number) => {
      setActiveStep(step);
    };

    // const handleNext = () => {
    //   setActiveStep((prevActiveStep) => prevActiveStep + 1);
    // };

    // const handleBack = () => {
    //   setActiveStep((prevActiveStep) => prevActiveStep - 1);
    // };

    return (
      <Box sx={{ width: width, height: height, flexGrow: 1, position: "relative", marginBottom: "57px" }}>
        <AutoPlaySwipeableViews
          axis="x"
          index={activeStep}
          onChangeIndex={handleStepChange}
          enableMouseEvents>
          {images.map((step, index) => (
            <div key={step.label} style={{ height: "100%", width: "100%" }}>
              {Math.abs(activeStep - index) <= 2 ? (
                <Box
                  component="div"
                  className={classes.imageBox}
                  sx={{ height: height, backgroundImage: `url(${step.imgPath})` }}>
                  <Box
                    className={classes.overlay}
                    sx={{ display: step.description || step.label ? "flex" : null, alignItems: "flex-end" }}>
                    {step.description || step.label ? (
                      <Box>
                        {step.description ? (
                          <Text typo="body 1" color="secondary" className={classes.description}>
                            {step.description}
                          </Text>
                        ) : null}
                        {step.label ? (
                          <Text typo="subtitle" color="focus" className={classes.title}>
                            {step.label}
                          </Text>
                        ) : null}
                      </Box>
                    ) : (
                      children
                    )}
                  </Box>
                </Box>
              ) : null}
            </div>
          ))}
        </AutoPlaySwipeableViews>
        <MobileStepper
          classes={{ dot: classes.dot, dotActive: classes.dotActive }}
          className={classes.steppers}
          steps={maxSteps}
          position="static"
          activeStep={activeStep}
          nextButton={null}
          backButton={null}
        />
      </Box>
    );
  })
);

const useStyles = makeStyles({ name: { SlideShow } })((theme) => ({
  root: {},
  overlay: {
    background:
      "linear-gradient(179.97deg, rgba(217, 217, 217, 0.3) -33.62%, rgba(255, 255, 255, 0.8) -33.61%, rgba(27, 27, 27, 0.8) 97.16%)",
    position: "absolute",
    top: "0",
    width: "100%",
    height: "100%",
    padding: theme.spacing(6) + theme.spacing(3),
  },
  steppers: {
    width: "100%",
    backgroundColor: "transparent",
    position: "absolute",
    bottom: "0",
    display: "flex",
    justifyContent: "center",
    paddingBottom: theme.spacing(6) + theme.spacing(3),
  },
  imageBox: {
    width: "100%",
    display: "block",
    overflow: "hidden",
    backgroundRepeat: "no-repeat",
    backgroundSize: "cover",
    backgroundPosition: "center",
  },
  title: {
    fontWeight: "bold",
    color: theme.colors.palette.light.main,
    paddingBottom: theme.spacing(4),
  },
  description: {
    color: theme.colors.palette.light.main,
    paddingBottom: theme.spacing(4),
  },
  dot: {
    backgroundColor: theme.colors.palette.light.main,
    opacity: 0.5,
  },
  dotActive: {
    backgroundColor: theme.colors.palette.light.main,
    opacity: 1,
  },
}));
