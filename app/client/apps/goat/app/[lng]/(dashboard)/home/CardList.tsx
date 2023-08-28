"use client";

import { makeStyles } from "@/lib/theme";
import { v4 } from "uuid";

import { Divider } from "@p4b/ui/components/DataDisplay/Divider";
import { CardContent, CardMedia, Card } from "@p4b/ui/components/Surfaces";
import { Button } from "@p4b/ui/components/theme";
import { Text } from "@p4b/ui/components/theme";

export interface CardType<IconId extends string> {
  title: string;
  description?: string;
  chips: string[];
  info?: {
    author: string;
    date: string;
  };
  icon?: IconId;
}

interface CardsDataArray {
  content: CardType<"file">;
  media: false | { image: string };
}

export interface CardListProps {
  title: string;
  buttons: string[];
  cards?: CardsDataArray[];
}

const CardList = (props: CardListProps) => {
  const { title, buttons, cards } = props;

  const { classes } = useStyles();

  return (
    <>
      <div className={classes.headerTitles}>
        <div>{title}</div>
        <div className={classes.buttons}>
          {buttons.map((button) => (
            <a href="@/app/[lng]/(dashboard)/home/CardList#" className={classes.button} key={v4()}>
              {button}
            </a>
          ))}
        </div>
      </div>
      <Divider width="100%" color="main" />
      <div className={classes.cardList}>
        {cards?.map((card) => (
          <Card
            key={v4()}
            width={268}
            aboveDivider={card.media ? <CardMedia src={card.media.image} alt="image" /> : false}>
            <CardContent {...card.content} />
          </Card>
        ))}
        {cards?.length && cards.length < 4 ? (
          <Card width={268} transparentBg={true}>
            <div className={classes.addButtonContainer}>
              <Button variant="ternary" className={classes.addButton}>
                <Text typo="label 1">+</Text>
                <Text typo="label 1" className={classes.addButtonText}>
                  New
                </Text>
              </Button>
            </div>
          </Card>
        ) : null}
      </div>
    </>
  );
};

const useStyles = makeStyles({ name: { CardList } })((theme) => ({
  cardList: {
    display: "flex",
    gap: theme.spacing(4),
    // justifyContent: "space-between",
    marginBottom: "57px",
  },
  headerTitles: {
    display: "flex",
    justifyContent: "space-between",
  },
  buttons: {
    display: "flex",
    gap: theme.spacing(3),
  },
  button: {
    border: "none",
    color: theme.colors.palette.focus.main,
    textDecoration: "none",
  },
  addButtonContainer: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    height: "100%",
  },
  addButton: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "3px",
    width: "100%",
    backgroundColor: theme.colors.useCases.surfaces.background,
    "&:hover": {
      backgroundColor: theme.isDarkModeEnabled
        ? theme.colors.palette.dark.greyVariant1
        : theme.colors.palette.light.greyVariant1,
    },
  },
  addButtonText: {
    // color: 'blue'
  },
}));

export default CardList;
