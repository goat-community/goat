"use client";

import { makeStyles } from "@/lib/theme";
import { postOrganizationSchema } from "@/lib/validations/organization";
import { zodResolver } from "@hookform/resolvers/zod";
import TextField from "@mui/material/TextField";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useRef } from "react";
import { useForm } from "react-hook-form";
import type * as z from "zod";

import { Alert } from "@p4b/ui/components/Alert";
import { SelectField } from "@p4b/ui/components/Inputs";
import { Card } from "@p4b/ui/components/Surfaces";
import { Button, Text } from "@p4b/ui/components/theme";

type FormData = z.infer<typeof postOrganizationSchema>;

type ResponseResult = {
  message: string;
  status?: "error" | "success";
};

export default function OrganizationCreate() {
  const router = useRouter();
  const { status, update } = useSession();
  const [isBusy, setIsBusy] = useState<boolean>(false);
  const [responseResult, setResponseResult] = useState<ResponseResult>({
    message: "",
    status: undefined,
  });
  const REGIONS = [
    {
      name: "EU",
      value: "eu",
    },
  ];

  const { classes } = useStyles();

  const submitButtonRef = useRef<HTMLButtonElement>(null);

  const {
    handleSubmit,
    register,
    formState: { errors, isDirty, isValid },
  } = useForm<FormData>({
    mode: "onChange",
    resolver: zodResolver(postOrganizationSchema),
    defaultValues: {
      region: "eu",
    },
  });

  async function onSubmit(data: FormData) {
    setResponseResult({ message: "", status: undefined });

    setIsBusy(true);
    const response = await fetch(`/api/auth/organizations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const responseJson = await response.json();
    setIsBusy(false);
    if (!response.ok) {
      setResponseResult({
        message: responseJson.detail,
        status: "error",
      });
      return;
    }
    update();
    router.push("/");
  }

  return (
    <>
      {status == "authenticated" && (
        <Card width={480} noHover={true} className={classes.paper}>
          <div className={classes.root}>
            <div className={classes.header}>
              <Text typo="page heading">Create organization</Text>
            </div>
            <form onSubmit={handleSubmit(onSubmit)}>
              {responseResult.status && (
                <Alert className={classes.alert} severity={responseResult.status}>
                  <Text typo="label 2">
                    <span>{responseResult.message}</span>
                  </Text>
                </Alert>
              )}
              <TextField
                helperText={errors.name ? errors.name?.message : null}
                label="Organization Name"
                id="name"
                {...register("name")}
                error={errors.name ? true : false}
              />
              <SelectField
                options={REGIONS}
                defaultValue={REGIONS[0].value}
                label="Region"
                size="medium"
                {...register("region")}
              />

              <div className={classes.buttonsWrapper}>
                <Button
                  ref={submitButtonRef}
                  className={classes.buttonSubmit}
                  name="login"
                  type="submit"
                  loading={isBusy}
                  disabled={!isDirty || !isValid || isBusy}>
                  Get started!
                </Button>
              </div>
            </form>
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
  header: {
    marginBottom: theme.spacing(4),
  },
  root: {
    margin: "32px",
    "& .MuiTextField-root": {
      width: "100%",
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(4),
    },
  },
  alert: {
    alignItems: "center",
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
