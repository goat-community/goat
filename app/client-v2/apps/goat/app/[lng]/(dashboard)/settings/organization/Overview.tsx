"use client";

import SubscriptionStatusCard from "@/app/[lng]/(dashboard)/settings/subscription/SubscriptionStatusCard";
import SubscriptionCardSkeleton from "@/components/skeletons/SubscriptionCardSkeleton";
import { OVERVIEW_API_URL } from "@/lib/api/apiConstants";
import { makeStyles } from "@/lib/theme";
import axios from "axios";
import React, { useRef } from "react";
import type { SubscriptionCard } from "subscriptions-dashboard";
import useSWR from "swr";
import { v4 } from "uuid";

import Dialog from "@p4b/ui/components/Dialog";
import { TextField } from "@p4b/ui/components/Inputs/TextField";
import Banner from "@p4b/ui/components/Surfaces/Banner";
import { Icon, Button, Text } from "@p4b/ui/components/theme";

const Overview = () => {
  // User state management
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);

  // styling related
  const dialogRef = useRef<HTMLDivElement>(null);
  const { classes } = useStyles();

  const UsersFetcher = (url: string) => {
    return axios(url).then((res) => res.data);
  };

  const { data, error, isLoading } = useSWR(OVERVIEW_API_URL, UsersFetcher);

  function openAddUserDialog(event: React.MouseEvent<HTMLButtonElement>) {
    setAnchorEl(event.currentTarget);
  }

  const handleAddUserClose = () => {
    setAnchorEl(null);
  };

  function beforeLoadedMessage() {
    if (isLoading) {
      return (
        <>
          <SubscriptionCardSkeleton />
        </>
      );
    } else if (error) {
      return "Error";
    } else {
      return "No results found!";
    }
  }

  function getOrganizationOverviewDetails(data: SubscriptionCard) {
    const visualData = {
      icon: data.icon,
      title: data.title,
      listItems: data.listItems.map((item: string) => (
        <Text typo="body 2" key={v4()}>
          {item}
        </Text>
      )),
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
                  iconId={data.icon}
                  size="small"
                  bgVariant="focus"
                  iconVariant="secondary"
                  wrapped="circle"
                  bgOpacity={0.6}
                />
                <Text className={classes.subheaderText} typo="body 1">
                  {data.title}
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
    return visualData;
  }

  return (
    <div>
      {!isLoading && !error ? (
        <SubscriptionStatusCard sectionData={getOrganizationOverviewDetails(data)} key={v4()} />
      ) : (
        beforeLoadedMessage()
      )}
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
