import React from "react";

import { makeStyles } from "../../lib/ThemeProvider";
import { Card } from "../Card";
import { TextField } from "../Text/TextField";
import { Text } from "../theme";
import { Button } from "../theme";

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
        <TextField label="Name" /> <TextField className={classes.textField} label="Email" />{" "}
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
    padding: "48px",
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
    margin: "24px 0",
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
