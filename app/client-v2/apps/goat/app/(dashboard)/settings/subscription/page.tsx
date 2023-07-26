"use client";

import { makeStyles } from "@/lib/theme";
import axios from "axios";
import type { SubscriptionCard } from "subscriptions-dashboard";
import useSWR from "swr";

import Banner from "@p4b/ui/components/Surfaces/Banner";
import { Button, Text } from "@p4b/ui/components/theme";

import SubscriptionStatusCard from "./SubscriptionStatusCard";
import type { SubscriptionStatusCardDataType } from "./SubscriptionStatusCard";

const Subscription = () => {
  const { classes } = useStyles();

  const UsersFetcher = (url: string) => {
    return axios(url).then((res) => res.data);
  };

  const { data, error, isLoading } = useSWR("/api/dashboard/subscription", UsersFetcher);

  function getSubscriptionDetails(datas: SubscriptionCard[]) {
    const visualData: SubscriptionStatusCardDataType[] = datas.map((data) => ({
      icon: data.icon,
      title: data.title,
      listItems: data.listItems.map((item: string, index: number) => (
        <Text typo="body 2" key={index}>
          {item}
        </Text>
      )),
      action: (
        <Button className={classes.button} variant="primary">
          Add seats
        </Button>
      ),
    }));
    return visualData;
  }

  function beforeLoadedMessage() {
    if (isLoading) {
      return "Loading...";
    } else if (error) {
      return "Error";
    } else {
      return "No results found!";
    }
  }

  return (
    <div>
      {!isLoading && !error ? (
        [...getSubscriptionDetails([data.subscription]), ...getSubscriptionDetails(data.extensions)].map(
          (extension, indx) => <SubscriptionStatusCard sectionData={extension} key={indx} />
        )
      ) : (
        <p>{beforeLoadedMessage()}</p>
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

const useStyles = makeStyles({ name: { Subscription } })((theme) => ({
  settingSection: {
    padding: theme.spacing(2),
  },
  tabs: {
    padding: "0",
  },
  bannerText: {
    color: "white",
    "@media (max-width: 1268px)": {
      fontSize: "14px",
    },
  },
  extensionButtonWrapper: {
    marginBottom: theme.spacing(5),
  },
  button: {
    marginTop: theme.spacing(3),
    padding: `${theme.spacing(1)}px ${theme.spacing(2) + 2}px`,
    fontSize: "13px",
  },
}));

export default Subscription;
