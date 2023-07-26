"use client";

import { makeStyles } from "@/lib/theme";
import React, { useRef } from "react";

import Dialog from "@p4b/ui/components/Dialog";
import { TextField } from "@p4b/ui/components/Inputs/TextField";
import Banner from "@p4b/ui/components/Surfaces/Banner";
import type { IconId } from "@p4b/ui/components/theme";
import { Icon, Button, Text } from "@p4b/ui/components/theme";

import SubscriptionStatusCard from "../subscription/SubscriptionStatusCard";

const Overview = () => {
  // User state management
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);

  // styling related
  const dialogRef = useRef<HTMLDivElement>(null);
  const { classes } = useStyles();

  function openAddUserDialog(event: React.MouseEvent<HTMLButtonElement>) {
    setAnchorEl(event.currentTarget);
  }

  const handleAddUserClose = () => {
    setAnchorEl(null);
  };

  const tempOrganisation: {
    title: string;
    icon: IconId;
    listItems: React.ReactNode[];
    action: React.ReactNode;
  } = {
    title: "Organisation name",
    icon: "coorperate",
    listItems: [
      <Text typo="body 2" key={1}>
        You are admin on this organisation
      </Text>,
      <Text typo="body 2" key={2}>
        12 active team members
      </Text>,
      <Text typo="body 2" key={3}>
        Active regions: Greater Munich, Greater London, Faux Valley, Stadtburg Burg
      </Text>,
    ],
    action: (
      <div className={classes.buttonWrapper}>
        <Button onClick={openAddUserDialog} className={classes.button} variant="primary">
          Manage license
        </Button>
        {anchorEl ? (
          <Dialog
            anchorEl={anchorEl}
            ref={dialogRef}
            onClick={handleAddUserClose}
            title="Update Oganizaztion Name"
            width="444px"
            direction="right"
            action={
              <div className={classes.buttons}>
                <Button variant="noBorder" onClick={handleAddUserClose}>
                  CANCEL
                </Button>
                <Button variant="noBorder">UPDATE</Button>
              </div>
            }>
            <div className={classes.subheader}>
              <Icon
                iconId="home"
                size="small"
                bgVariant="focus"
                iconVariant="secondary"
                wrapped="circle"
                bgOpacity={0.6}
              />
              <Text className={classes.subheaderText} typo="body 1">
                Organization name
              </Text>
            </div>
            <div className={classes.formInputs}>
              <TextField type="text" label="New name" />
              <TextField type="password" label="Confirm password" />
            </div>
          </Dialog>
        ) : null}
      </div>
    ),
  };

  return (
    <div>
      <SubscriptionStatusCard sectionData={tempOrganisation} />
      <Banner
        actions={<Button>Subscribe Now</Button>}
        content={
          <Text className={classes.bannerText} typo="body 1">
            Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
            massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.{" "}
          </Text>
        }
        image="https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4"
        imageSide="right"
      />
      {/* {[subscriptionStatus, ...extensions].map((extension, indx) => (
          ))}
          <div className={classes.extensionButtonWrapper}>
            {!isDemo ? <Button>Add extensions</Button> : null}
          </div>
           */}
    </div>
  );
};

const useStyles = makeStyles({ name: { Overview } })((theme) => {
  return {
    bannerText: {
      color: "white",
      "@media (max-width: 1268px)": {
        fontSize: "14px",
      },
    },
    button: {
      marginTop: theme.spacing(3),
      padding: `${theme.spacing(1)}px ${theme.spacing(2) + 2}px`,
      fontSize: "13px",
    },
    buttonWrapper: {
      position: "relative",
    },
    subheader: {
      display: "flex",
      marginBottom: theme.spacing(3),
    },
    subheaderText: {
      marginLeft: theme.spacing(2),
    },
    formInputs: {
      display: "flex",
      flexDirection: "column",
      gap: theme.spacing(2),
    },
    buttons: {
      display: "flex",
      justifyContent: "end",
      gap: theme.spacing(1),
    },
  };
});

export default Overview;
