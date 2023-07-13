import { useState, useEffect, useRef } from "react";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { SelectField } from "../../../Inputs/SelectField";
import { TextField } from "../../../Inputs/TextField";
import { Card } from "../../../Surfaces";
import { Button, Text } from "../../../theme";

export default function Create() {
  const { classes } = useStyles();

  // refs
  const organizationInputRef = useRef<HTMLInputElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);

  // Component States
  const [selectedIndustry, setSelectedIndustry] = useState<string | string[]>("gis");

  useEffect(() => {
    console.log(selectedIndustry && organizationInputRef?.current?.value === "");
  }, [selectedIndustry, organizationInputRef?.current?.value]);

  // functions
  const onSubmit = () => {
    console.log("submit");
  };

  const Industries = [
    {
      name: "Transport Planing",
      value: "transportPlaning",
    },
    {
      name: "Urban Planing",
      value: "urbanPlaning",
    },
    {
      name: "GIS",
      value: "gis",
    },
    {
      name: "Architecture",
      value: "Architecture",
    },
  ];

  return (
    <>
      <Text typo="subtitle" className={classes.headerText} color="focus">
        Complete your account setup
      </Text>
      <div className={classes.CardContainer}>
        <Card width={480} noHover={true}>
          <div className={classes.root}>
            <div>
              <div>
                <Text typo="section heading">Create organization</Text>
              </div>
              <form onSubmit={onSubmit} method="post">
                <div>
                  <TextField
                    disabled={false}
                    id="organizationName"
                    name="organizationName"
                    inputProps_ref={organizationInputRef}
                    inputProps_aria-label="text"
                    inputProps_tabIndex={1}
                    inputProps_spellCheck={false}
                    label="Organization name"
                    autoComplete="off"
                    size="medium"
                  />
                  <Text typo="body 3" className={classes.inputMessage}>
                    Select a recognisable name for your teammates
                  </Text>
                </div>
                <div>
                  <SelectField
                    updateChange={setSelectedIndustry}
                    size="medium"
                    options={Industries}
                    defaultValue={[selectedIndustry].flat().join(", ")}
                    label="Industry"
                  />
                </div>
                <div className={classes.buttonsWrapper}>
                  <input type="hidden" name="credentialId" />
                  <Button
                    ref={submitButtonRef}
                    className={classes.buttonSubmit}
                    name="login"
                    type="submit"
                    disabled={selectedIndustry && organizationInputRef?.current?.value !== "" ? false : true}>
                    Continue
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}

const useStyles = makeStyles({ name: { Create } })((theme) => ({
  root: {
    margin: "32px",
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(5),
    },
  },
  inputMessage: {
    paddingLeft: "12px",
    marginBottom: theme.spacing(3),
  },
  buttonsWrapper: {
    marginTop: theme.spacing(4),
    display: "flex",
    justifyContent: "flex-end",
  },
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(2),
    marginLeft: theme.spacing(0),
  },
  divider: {
    ...theme.spacing.topBottom("margin", 5),
  },
  headerText: {
    margin: `${theme.spacing(5)}px auto`,
    textAlign: "center",
    fontSize: "34px",
    fontWeight: "800 ",
  },
  CardContainer: {
    display: "flex",
    justifyContent: "center",
  },
}));

const { LoginDivider } = (() => {
  type Props = {
    className?: string;
  };

  function LoginDivider(props: Props) {
    const { className } = props;

    const { classes, cx } = useStyles();

    const separator = <div role="separator" className={classes.separator} />;

    return (
      <div className={cx(classes.root, className)}>
        {separator}
        <Text typo="body 2" color="secondary" className={classes.text}>
          Or
        </Text>
        {separator}
      </div>
    );
  }

  const useStyles = makeStyles({ name: { LoginDivider } })((theme) => ({
    root: {
      display: "flex",
      alignItems: "center",
    },
    separator: {
      height: 1,
      backgroundColor: theme.colors.useCases.typography.textSecondary,
      flex: 1,
    },
    text: {
      ...theme.spacing.rightLeft("margin", 2),
      paddingBottom: 2,
    },
  }));

  return { LoginDivider };
})();
