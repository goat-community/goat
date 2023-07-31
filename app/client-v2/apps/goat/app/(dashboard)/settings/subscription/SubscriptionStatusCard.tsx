import { makeStyles } from "@/lib/theme";
import type { SubscriptionStatusCardDataType } from "subscriptions-dashboard";
import { v4 } from "uuid";

import { Card } from "@p4b/ui/components/Surfaces/Card";
import { Icon, Text } from "@p4b/ui/components/theme";

interface SubscriptionStatusCardProps {
  sectionData: SubscriptionStatusCardDataType;
}

const SubscriptionStatusCard = (props: SubscriptionStatusCardProps) => {
  const { sectionData } = props;

  const { classes } = useStyles();
  return (
    <>
      <Card width="100%" className={classes.settingSection} noHover={true}>
        <div className={classes.headerSection}>
          <Icon
            iconId={sectionData.icon}
            size="medium"
            bgVariant="focus"
            iconVariant="focus"
            wrapped="circle"
          />
          <Text typo="body 1" className={classes.title}>
            {sectionData.title}
          </Text>
        </div>
        <div className={classes.flexWrapper}>
          <ul style={{ paddingLeft: "30px" }}>
            {sectionData.listItems.map((listItam: React.ReactNode) => (
              <li style={{ paddingBottom: "12.5px" }} key={v4()}>
                {listItam}
              </li>
            ))}
          </ul>
          {sectionData.action}
        </div>
      </Card>
    </>
  );
};

const useStyles = makeStyles({ name: { SubscriptionStatusCard } })((theme) => ({
  settingSection: {
    padding: `0px ${theme.spacing(3)}px`,
    marginBottom: theme.spacing(5),
  },
  title: {
    fontWeight: "bold",
  },
  headerSection: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    padding: `${theme.spacing(2)}px 0px`,
  },
  icon: {
    color: theme.colors.palette.focus.main,
  },
  lastListItem: {
    marginBottom: theme.spacing(5), //32
  },
  flexWrapper: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "start",
  },
}));

export default SubscriptionStatusCard;
