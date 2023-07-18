"use client";

import { makeStyles } from "@/lib/theme";
import { signIn } from "next-auth/react";
import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";

import { Button, Text } from "@p4b/ui/components/theme";

export default function Login() {
  const { classes } = useStyles();
  const { status } = useSession();

  console.log("status", status);
  if (status === "authenticated") {
    redirect(`/`);
  }

  return (
    <>
      <div className={classes.root}>
        <Text typo="section heading">Welcome back!</Text>
        <Text typo="body 1" color="secondary" className={classes.loginDescription}>
          Access the most up-to-date version of GOAT, ensuring a seamless and fully cloud-native user
          experience.
        </Text>
        <div className={classes.buttonsWrapper}>
          <Button
            onClick={() => signIn("keycloak")}
            variant="primary"
            className={classes.buttonSubmit}
            name="login"
            type="submit">
            Log in to GOAT
          </Button>
        </div>
      </div>
    </>
  );
}

const useStyles = makeStyles({ name: { Login } })((theme) => ({
  root: {
    margin: "32px",
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(6),
      marginBottom: theme.spacing(6),
    },
  },
  loginDescription: {
    marginTop: theme.spacing(4),
    marginBottom: theme.spacing(4),
  },
  linkToRegisterWrapper: {
    marginTop: theme.spacing(5),
    textAlign: "left",
    "& > *": {
      display: "inline-block",
    },
  },
  registerLink: {
    paddingLeft: theme.spacing(2),
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
}));
