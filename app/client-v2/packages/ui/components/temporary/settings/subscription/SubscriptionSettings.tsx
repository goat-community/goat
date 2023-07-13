import { makeStyles } from "../../../../lib/ThemeProvider";
import Subscription from "./Subscription";

const SubscriptionSettings = () => {
  const { classes, cx } = useStyles();

  return (
    <>
      <Subscription />
    </>
  );
};

const useStyles = makeStyles({ name: { SubscriptionSettings } })((theme) => ({}));

export default SubscriptionSettings;
