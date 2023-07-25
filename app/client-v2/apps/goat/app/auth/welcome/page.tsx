"use client";

import { makeStyles } from "@/lib/theme";
import { useSession } from "next-auth/react";

import { Card } from "@p4b/ui/components/Surfaces";
import { Text } from "@p4b/ui/components/theme";

export default function OrganizationCreate() {
  const { classes } = useStyles();
  const { status } = useSession();

  return (
    <>
      {status == "authenticated" && (
        <Card width={480} noHover={true} className={classes.paper}>
          <div className={classes.root}>
            <div>
              <Text typo="section heading">Your account has been successfully validated</Text>
            </div>
          </div>
        </Card>
      )}
    </>
  );
}

const useStyles = makeStyles({ name: { OrganizationCreate } })((theme) => ({
  paper: {
    padding: theme.spacing(5),
    width: 490,
    height: "fit-content",
    marginBottom: theme.spacing(4),
    borderRadius: 4,
  },
  root: {
    margin: "32px",
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(6),
      marginBottom: theme.spacing(6),
    },
  },
}));
