import { Stepper as MUIStepper } from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Step from "@mui/material/Step";
import StepButton from "@mui/material/StepButton";
import Typography from "@mui/material/Typography";
import { useImperativeHandle } from "react";
import * as React from "react";
import { forwardRef } from "react";

import { makeStyles } from "../lib/ThemeProvider";

interface StepperProps {
  className?: string;
  steps: { label: string; child: React.ReactNode }[];
  customActions?: React.ReactNode;
}
// React.forwardRef(({ actionButtons, ...props }, ref)
const Stepper = forwardRef((props: StepperProps, ref) => {
  const { className, steps, customActions } = props;
  const { classes } = useStyles();
  const [activeStep, setActiveStep] = React.useState(0);
  const [completed, setCompleted] = React.useState<{
    [k: number]: boolean;
  }>({});

  const totalSteps = () => {
    return steps.length;
  };

  const completedSteps = () => {
    return Object.keys(completed).length;
  };

  const isLastStep = () => {
    return activeStep === totalSteps() - 1;
  };

  const allStepsCompleted = () => {
    return completedSteps() === totalSteps();
  };

  const handleNext = () => {
    const newActiveStep =
      isLastStep() && !allStepsCompleted()
        ? // It's the last step, but not all steps have been completed,
          // find the first step that has been completed
          steps.findIndex((step, i) => !(i in completed))
        : activeStep + 1;

    if (isPrevCompleted()) {
      setActiveStep(newActiveStep);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleStep = (step: number) => () => {
    if (isPrevCompleted() || completed[step]) {
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

  const isPrevCompleted = () => {
    if (completed[activeStep]) {
      return true;
    }
    return false;
  };

  useImperativeHandle(ref, () => ({
    handleComplete,
  }));

  return (
    <Box sx={{ width: "100%" }}>
      <MUIStepper nonLinear activeStep={activeStep} className={className}>
        {steps.map((step, index) => (
          <Step key={index} completed={completed[index]}>
            <StepButton color="inherit" onClick={handleStep(index)}>
              <p style={{ fontSize: "14px", margin: "0" }}>{step.label}</p>
            </StepButton>
          </Step>
        ))}
      </MUIStepper>
      <div>
        {allStepsCompleted() ? (
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
                      {completedSteps() === totalSteps() - 1 ? "Finish" : "Complete Step"}
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

const useStyles = makeStyles({ name: { Stepper } })((theme) => ({
  root: {},
}));

Stepper.displayName = "Stepper";

export default Stepper;
