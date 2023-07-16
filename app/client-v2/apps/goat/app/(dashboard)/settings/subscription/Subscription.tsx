import { makeStyles } from "@/lib/theme";
import { useState } from "react";

import Banner from "@p4b/ui/components/Banner";
import { Button, Text } from "@p4b/ui/components/theme";

import SubscriptionStatusCard from "./SubscriptionStatusCard";
import type { SubscriptionStatusCardDataType } from "./SubscriptionStatusCard";

const Subscription = () => {
  const { classes } = useStyles();

  const [subscriptionDetails, setSubscriptionDetails] = useState<SubscriptionStatusCardDataType>({
    icon: "rocketLaunch",
    title: "Starter",
    listItems: [
      <Text typo="body 2" key={1}>
        Next payment: 23 July 2024
      </Text>,
      <Text typo="body 2" key={2}>
        Annual payment cycle: 23 July 2023 - 23 July 2024
      </Text>,
      <Text typo="body 2" key={3}>
        2 of 12 editors seat available
      </Text>,
      <Text typo="body 2" key={4}>
        Region: Greater Munich
      </Text>,
    ],
    action: (
      <Button className={classes.button} variant="primary">
        Add seats
      </Button>
    ),
  });

  const subscriptionExtensions: SubscriptionStatusCardDataType[] = [
    {
      icon: "run",
      title: "Active mobility",
      listItems: [
        <Text typo="body 2" key={1}>
          Next payment: 23 July 2024
        </Text>,
        <Text typo="body 2" key={2}>
          Annual payment cycle: 23 July 2023 - 23 July 2024
        </Text>,
        <Text typo="body 2" key={3}>
          2 of 12 editors seat available
        </Text>,
        <Text typo="body 2" key={4}>
          Region: Greater Munich
        </Text>,
      ],
      action: (
        <Button className={classes.button} variant="primary">
          Add seats
        </Button>
      ),
    },
    {
      icon: "bus",
      title: "Motorised mobility",
      listItems: [
        <Text typo="body 2" key={1}>
          Next payment: 23 July 2024
        </Text>,
        <Text typo="body 2" key={2}>
          Annual payment cycle: 23 July 2023 - 23 July 2024
        </Text>,
        <Text typo="body 2" key={3}>
          2 of 12 editors seat available
        </Text>,
        <Text typo="body 2" key={4}>
          Region: Greater Munich
        </Text>,
      ],
      action: (
        <Button className={classes.button} variant="primary">
          Add seats
        </Button>
      ),
    },
  ];

  return (
    <div>
      {[subscriptionDetails, ...subscriptionExtensions].map((extension, indx) => (
        <SubscriptionStatusCard sectionData={extension} key={indx} />
      ))}
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
