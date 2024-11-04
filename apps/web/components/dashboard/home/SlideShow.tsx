import { Box, CardMedia, Typography } from "@mui/material";
import Carousel from "react-material-ui-carousel";

const slideShowImages = [
  {
    imgPath: "https://source.unsplash.com/random",
    label: "Lorem ipsum CTA1",
    description:
      "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.",
  },
  {
    imgPath: "https://source.unsplash.com/random",
    label: "Lorem ipsum CTA2",
    description:
      "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.",
  },
  {
    imgPath: "https://source.unsplash.com/random",
    label: "Lorem ipsum CTA3",
    description:
      "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.",
  },
];

const FeedSlideShow = () => {
  const items = slideShowImages;
  return (
    <Carousel indicators={false}>
      {items.map((item, i) => (
        <>
          <CardMedia
            key={i}
            image={item.imgPath}
            title={item.label}
            style={{ height: "300px", width: "100%", objectFit: "cover" }}>
            <Box
              sx={{
                px: 8,
                pb: 8,
                position: "absolute",
                bottom: 0,
                left: 0,
                width: "100%",
                bgcolor: "rgba(0, 0, 0, 0)",
                color: "white",
              }}>
              <Typography variant="body1">{item.description}</Typography>
              <Typography variant="h5" sx={{ mt: 8 }}>
                {item.label}
              </Typography>
            </Box>
          </CardMedia>
        </>
      ))}
    </Carousel>
  );
};

export default FeedSlideShow;
