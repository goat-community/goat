"use client";

import { makeStyles } from "@/lib/theme";

import { TextField } from "@p4b/ui/components/Inputs";
import { Card } from "@p4b/ui/components/Surfaces";
import { Text } from "@p4b/ui/components/theme";
import { Button } from "@p4b/ui/components/theme";

const NewsLetterSection = () => {
  const { classes, cx } = useStyles();

  return (
    <Card className={classes.card} transparentBg>
      <div>
        <Text typo="section heading" className={cx(classes.header, classes.text)}>
          Keep up with GOAT & Plan4Better latest updates, join our Newsletter
        </Text>
      </div>
      <div className={classes.formSection}>
        <TextField size="small" label="Name" />{" "}
        <TextField size="small" className={classes.textField} label="Email" />{" "}
        <Button className={classes.button} variant="ternary">
          Subscribe
        </Button>
      </div>
      <div>
        <Text typo="body 2" className={classes.text}>
          Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean massa. Cum sociis natoque penatibus
          et magnis dis parturient montes{" "}
        </Text>
      </div>
    </Card>
  );
};

const useStyles = makeStyles({ name: { NewsLetterSection } })((theme) => ({
  card: {
    width: "100%",
    padding: theme.spacing(6) + theme.spacing(3),
    border: `1px solid ${theme.colors.palette.dark.greyVariant2}10`,
  },
  textField: {
    width: "400px",
  },
  formSection: {
    display: "flex",
    justifyContent: "center",
    gap: "12px",
    alignItems: "center",
    margin: `${theme.spacing(4)}px 0`,
  },
  text: {
    textAlign: "center",
  },
  header: {
    fontWeight: "bolder",
  },
  button: {
    padding: "8px 24px",
  },
}));

export default NewsLetterSection;
