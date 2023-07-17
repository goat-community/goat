"use client";

import { makeStyles } from "@/lib/theme";
import { useState, useRef } from "react";

import { Card } from "@p4b/ui/components/Card";
import { SelectField } from "@p4b/ui/components/SelectField";
import { TextField } from "@p4b/ui/components/Text/TextField";
import { Button, Text } from "@p4b/ui/components/theme";

export default function OrganizationCreate() {
  const [selectedIndustry, setSelectedIndustry] = useState("gis");

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

  const onSubmit = () => {
    console.log("submit");
  };

  const { classes } = useStyles();

  const organizationInputRef = useRef<HTMLInputElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);

  return (
    <>
      <div className={classes.cardContainer}>
        <Card width={480} noHover={true}>
          <div className={classes.root}>
            <div>
              <div>
                <Text typo="section heading">Create organization</Text>
              </div>
              <form onSubmit={onSubmit} method="post">
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
                />

                <SelectField
                  className={classes.selectField}
                  updateChange={setSelectedIndustry}
                  options={Industries}
                  defaultValue={selectedIndustry}
                  label="Industry"
                  size="medium"
                />

                <div className={classes.buttonsWrapper}>
                  <Button
                    ref={submitButtonRef}
                    className={classes.buttonSubmit}
                    name="login"
                    type="submit"
                    disabled={selectedIndustry && organizationInputRef?.current?.value !== "" ? false : true}>
                    Get started!
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

const useStyles = makeStyles({ name: { OrganizationCreate } })((theme) => ({
  root: {
    margin: "32px",
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(6),
      marginBottom: theme.spacing(6),
    },
  },
  selectField: {
    width: "100%",
    marginTop: theme.spacing(5),
  },
  buttonsWrapper: {
    marginTop: theme.spacing(4),
    display: "flex",
    justifyContent: "flex-end",
  },
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(4),
    marginLeft: theme.spacing(0),
  },
  divider: {
    ...theme.spacing.topBottom("margin", 5),
  },
  cardContainer: {
    display: "flex",
    justifyContent: "center",
  },
}));
