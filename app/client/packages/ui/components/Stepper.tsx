import { Stepper as MUIStepper } from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Step from "@mui/material/Step";
import StepButton from "@mui/material/StepButton";
import Typography from "@mui/material/Typography";
import { useImperativeHandle } from "react";
import * as React from "react";
import { forwardRef } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../lib/ThemeProvider";

type Steps = { label: string; child: React.ReactNode };
interface StepperProps {
  className?: string;
  steps: Steps[];
  customActions?: React.ReactNode;
}
// React.forwardRef(({ actionButtons, ...props }, ref)
const Stepper = forwardRef((props: StepperProps, ref) => {
  const { className, steps, customActions } = props;
  const { classes } = useStyles();

  // Component States
  const [activeStep, setActiveStep] = React.useState(0);
  const [completed, setCompleted] = React.useState<{
    [k: number]: boolean;
  }>({});

  // Functions
  const handleNext = () => {
    const newActiveStep =
      isLastStep(activeStep, steps) && !allStepsCompleted(completed, steps)
        ? // It's the last step, but not all steps have been completed,
          // find the first step that has been completed
          steps.findIndex((_, i) => !(i in completed))
        : activeStep + 1;

    if (isPrevCompleted(completed, activeStep)) {
      setActiveStep(newActiveStep);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleStep = (step: number) => () => {
    if (isPrevCompleted(completed, activeStep) || completed[step]) {
      setActiveStep(step);
    }
  };

  const handleComplete = () => {
    const newCompleted = completed;
    newCompleted[activeStep] = true;
    setCompleted(newCompleted);
    handleNext();
  };

  const handleReset = () => {
    setActiveStep(0);
    setCompleted({});
  };

  useImperativeHandle(ref, () => ({
    handleComplete,
  }));

  return (
    <Box sx={{ width: "100%" }}>
      <MUIStepper nonLinear activeStep={activeStep} className={className}>
        {steps.map((step, index) => (
          <Step className={classes.root} key={v4()} completed={completed[index]}>
            <StepButton color="inherit" onClick={handleStep(index)}>
              <p style={{ fontSize: "14px", margin: "0" }}>{step.label}</p>
            </StepButton>
          </Step>
        ))}
      </MUIStepper>
      <div>
        {allStepsCompleted(completed, steps) ? (
          <React.Fragment>
            <Typography sx={{ mt: 2, mb: 1 }}>All steps completed - you&apos;re finished</Typography>
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Box sx={{ flex: "1 1 auto" }} />
              <Button onClick={handleReset}>Reset</Button>
            </Box>
          </React.Fragment>
        ) : (
          <React.Fragment>
            <Box>{steps[activeStep].child}</Box>
            {!customActions ? (
              <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
                <Button color="inherit" disabled={activeStep === 0} onClick={handleBack} sx={{ mr: 1 }}>
                  Back
                </Button>
                <Box sx={{ flex: "1 1 auto" }} />
                <Button onClick={handleNext} sx={{ mr: 1 }}>
                  Next
                </Button>
                {activeStep !== steps.length &&
                  (completed[activeStep] ? (
                    <Typography variant="caption" sx={{ display: "inline-block" }}>
                      Step {activeStep + 1} already completed
                    </Typography>
                  ) : (
                    <Button onClick={handleComplete}>
                      {completedSteps(completed) === totalSteps(steps) - 1 ? "Finish" : "Complete Step"}
                    </Button>
                  ))}
              </Box>
            ) : (
              customActions
            )}
          </React.Fragment>
        )}
      </div>
    </Box>
  );
});

const useStyles = makeStyles({ name: { Stepper } })(() => ({
  root: {
    "& .css-1e7c4pk-MuiStepIcon-text": {
      fill: "#fff",
    },
    "& .mui-1e7c4pk-MuiStepIcon-text": {
      color: "#fff",
    },
  },
}));

// helper functions
const totalSteps = (steps: Steps[]) => {
  return steps.length;
};

const completedSteps = (completed: { [k: number]: boolean }) => {
  return Object.keys(completed).length;
};

const isLastStep = (activeStep: number, steps: Steps[]) => {
  return activeStep === totalSteps(steps) - 1;
};

const allStepsCompleted = (completed: { [k: number]: boolean }, steps: Steps[]) => {
  return completedSteps(completed) === totalSteps(steps);
};

const isPrevCompleted = (completed: { [k: number]: boolean }, activeStep: number) => {
  if (completed[activeStep]) {
    return true;
  }
  return false;
};

Stepper.displayName = "Stepper";

export default Stepper;
