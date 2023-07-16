import { makeStyles } from "@/lib/theme";
import { useEffect, useState } from "react";

import Banner from "@p4b/ui/components/Banner";
import { Button, Text } from "@p4b/ui/components/theme";

import SubscriptionStatusCard from "./SubscriptionStatusCard";
import type { SubscriptionStatusCardDataType } from "./SubscriptionStatusCard";

const Overview = () => {
  const { classes } = useStyles();
  const [isDemo, setIsDemo] = useState<boolean | null>(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatusCardDataType>({
    icon: "rocketLaunch",
    title: "Starter",
    listItems: [
      <Text typo="body 2" key={1}>
        2 of 12 seats available
      </Text>,
    ],
    action: (
      <Button className={classes.button} variant="secondary">
        Manage seats
      </Button>
    ),
  });

  const extensions: SubscriptionStatusCardDataType[] = [
    {
      icon: "run",
      title: "Active mobility",
      listItems: [
        <Text typo="body 2" key={1}>
          Great Munich Area - 6 of 10 editors available
        </Text>,
      ],
      action: (
        <Button className={classes.button} variant="secondary">
          Manage seats
        </Button>
      ),
    },
    {
      icon: "bus",
      title: "Motorised mobility",
      listItems: [
        <Text typo="body 2" key={1}>
          Great Munich Area - 4 of 10 editors available
        </Text>,
      ],
      action: (
        <Button className={classes.button} variant="secondary">
          Manage seats
        </Button>
      ),
    },
  ];

  useEffect(() => {
    setIsDemo(false);
  });

  return (
    <div>
      {[subscriptionStatus, ...extensions].map((extension, indx) => (
        <SubscriptionStatusCard sectionData={extension} key={indx} />
      ))}
      <div className={classes.extensionButtonWrapper}>{!isDemo ? <Button>Add extensions</Button> : null}</div>
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

const useStyles = makeStyles({ name: { Overview } })((theme) => ({
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

export default Overview;
