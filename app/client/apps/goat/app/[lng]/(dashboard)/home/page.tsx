"use client";

import GridContainer from "@/components/grid/GridContainer";
import SingleGrid from "@/components/grid/SingleGrid";
import { makeStyles } from "@/lib/theme";
import { v4 } from "uuid";

import Box from "@p4b/ui/components/Box";
import { SlideShow } from "@p4b/ui/components/SlideShow";

import CardList, { type CardType } from "./CardList";
import NewsLetterSection from "./NewsLetterSection";

interface CardsDataArray {
  content: CardType<"file">;
  media: false | { image: string };
}

interface CardDataType {
  title: string;
  cards: CardsDataArray[];
  buttons: string[];
}

const Home = () => {
  const { classes } = useStyles();

  // Project Dumb Data
  const tempCardInfo: CardDataType[] = [
    {
      buttons: ["See all"],
      title: "Recent Projects",
      cards: [
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Project title",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Project title",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Project title",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
      ],
    },
    {
      buttons: ["See all"],
      title: "Recent Contents",
      cards: [
        {
          content: {
            icon: "file",
            title: "Content title",
            description: "content_file_title.extension",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: false,
        },
        {
          content: {
            icon: "file",
            title: "Content title",
            description: "content_file_title.extension",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: false,
        },
        {
          content: {
            icon: "file",
            title: "Content title",
            description: "content_file_title.extension",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: false,
        },
        {
          content: {
            icon: "file",
            title: "Content title",
            description: "content_file_title.extension",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: false,
        },
      ],
    },
    {
      title: "Explore",
      buttons: ["BLOG", "DOCUMENTATION", "TUTORIALS", "USE CASES", "NEWS"],
      cards: [
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Label",
            description:
              "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Label",
            description:
              "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Label",
            description:
              "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
        {
          content: {
            info: {
              author: "John Doe",
              date: "4 Feb 2022",
            },
            title: "Label",
            description:
              "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.",
            chips: ["Chip", "Chip", "Chip", "Chip", "Chip"],
          },
          media: {
            image:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
          },
        },
      ],
    },
  ];

  const slideShowImages = [
    {
      imgPath:
        "https://s3-alpha-sig.figma.com/img/780f/4ef5/c934bfac69cba006cec203491b616d85?Expires=1685923200&Signature=IhTpFXcdFrI7Xx9wBP2mnRbKsYiKP2c-r~lwmayIrxsWscWQ0eo7WzG0J5rhY~291iaTghdizAq3qTqkSnov4kvqAPL6YCdslajCk2r7wFZXabXTQnxtDYHGui~bDFp5gu5bFIztlA4ClUWikpjdDu54eT1VBGUID68mt6t~UnLXUVOV-D6S526gcJKMDUt~8bJeCl3knMQrr27-9520~-FNebfh7qI37hScTL9z1ugXKHr2ndqngGsdfAaGQR-iPaXqC2l1W5xEALtFX6KB8HMbLV88hGddnQIVSodwgFKgznxIcWPf48i5DUpebZuq08zMo0~CtvJ44O1QBWQH9g__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
      label: "Lorem ipsum CTA1",
      description:
        "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.",
    },
    {
      imgPath:
        "https://s3-alpha-sig.figma.com/img/780f/4ef5/c934bfac69cba006cec203491b616d85?Expires=1685923200&Signature=IhTpFXcdFrI7Xx9wBP2mnRbKsYiKP2c-r~lwmayIrxsWscWQ0eo7WzG0J5rhY~291iaTghdizAq3qTqkSnov4kvqAPL6YCdslajCk2r7wFZXabXTQnxtDYHGui~bDFp5gu5bFIztlA4ClUWikpjdDu54eT1VBGUID68mt6t~UnLXUVOV-D6S526gcJKMDUt~8bJeCl3knMQrr27-9520~-FNebfh7qI37hScTL9z1ugXKHr2ndqngGsdfAaGQR-iPaXqC2l1W5xEALtFX6KB8HMbLV88hGddnQIVSodwgFKgznxIcWPf48i5DUpebZuq08zMo0~CtvJ44O1QBWQH9g__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
      label: "Lorem ipsum CTA2",
      description:
        "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.",
    },
    {
      imgPath:
        "https://s3-alpha-sig.figma.com/img/780f/4ef5/c934bfac69cba006cec203491b616d85?Expires=1685923200&Signature=IhTpFXcdFrI7Xx9wBP2mnRbKsYiKP2c-r~lwmayIrxsWscWQ0eo7WzG0J5rhY~291iaTghdizAq3qTqkSnov4kvqAPL6YCdslajCk2r7wFZXabXTQnxtDYHGui~bDFp5gu5bFIztlA4ClUWikpjdDu54eT1VBGUID68mt6t~UnLXUVOV-D6S526gcJKMDUt~8bJeCl3knMQrr27-9520~-FNebfh7qI37hScTL9z1ugXKHr2ndqngGsdfAaGQR-iPaXqC2l1W5xEALtFX6KB8HMbLV88hGddnQIVSodwgFKgznxIcWPf48i5DUpebZuq08zMo0~CtvJ44O1QBWQH9g__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
      label: "Lorem ipsum CTA3",
      description:
        "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.",
    },
  ];

  return (
    <Box className={classes.root}>
      <GridContainer>
        <SingleGrid span={4}>
          <SlideShow images={slideShowImages} height={328} width="100%" />
          {tempCardInfo.map((cardSection: CardDataType) => (
            <CardList
              title={cardSection.title}
              cards={cardSection.cards}
              buttons={cardSection.buttons}
              key={v4()}
            />
          ))}
          <NewsLetterSection />
        </SingleGrid>
      </GridContainer>
    </Box>
  );
};

const useStyles = makeStyles({ name: { Home } })(() => ({
  root: {
    marginTop: "100px",
  },
  media: {
    width: "100%",
    height: "100px",
    borderTopRightRadius: 4,
    borderTopLeftRadius: 4,
    objectFit: "cover",
  },
}));

export default Home;
