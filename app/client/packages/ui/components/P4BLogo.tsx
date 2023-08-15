import { Box } from "@mui/material";

interface P4BLogoProps {
  absolute?: boolean;
  width?: number;
}

const P4BLogo = (props: P4BLogoProps) => {
  const { absolute = false, width = 160 } = props;

  return (
    <Box
      component="header"
      sx={{
        left: 0,
        p: absolute ? 3 : 0,
        position: absolute ? "absolute" : "static",
        top: 0,
        width: "100%",
      }}>
      <Box
        component="a"
        href="https://www.plan4better.de/"
        target="_blank"
        sx={{
          display: "inline-flex",
          width: width,
        }}>
        <img
          width="100%"
          src="https://assets.plan4better.de/img/logo/plan4better_white.svg"
          alt="Plan4Better Logo"
        />
      </Box>
    </Box>
  );
};

export default P4BLogo;
