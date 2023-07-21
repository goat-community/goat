import React from "react";

import { TextField } from "@p4b/ui/components/Inputs";
import { Text, Icon } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface InviteUserProps {
  setEmail: (value: string) => void;
}

const InviteUser = (props: InviteUserProps) => {
  const { setEmail } = props;

  const { classes } = useStyles();

  return (
    <div>
      <div className={classes.head}>
        <Icon
          iconId="home"
          wrapped="circle"
          bgVariant="focus"
          bgOpacity={0.6}
          iconVariant="secondary"
          size="small"
        />
        <Text typo="body 1">Organization name</Text>
      </div>
      <Text typo="body 2">
        Send an invitation via email <br /> The receiver will get a link with 72 hours of expiration
      </Text>
      <div className={classes.formInputs}>
        <TextField
          size="small"
          type="email"
          label="Email address"
          onValueBeingTypedChange={({ value }) => setEmail(value)}
        />
      </div>
    </div>
  );
};

const useStyles = makeStyles({ name: { InviteUser } })((theme) => ({
  formInputs: {
    marginTop: theme.spacing(3),
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(2),
  },
  head: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
  },
}));

export default InviteUser;
