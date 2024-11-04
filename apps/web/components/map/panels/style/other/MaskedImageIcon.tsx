import type { BoxProps } from "@mui/material";
import { Box } from "@mui/material";
import { styled } from "@mui/material/styles";

const StyledBox = styled(Box)(({ theme }) => ({
  display: "inline-flex",
  alignContent: "center",
  maskRepeat: "no-repeat",
  maskSize: "contain",
  backgroundColor: theme.palette.text.secondary,
  backgroundRepeat: "no-repeat",
  backgroundSize: "contain",
  flexShrink: 0,
}));

export interface ImageProps extends Omit<BoxProps, "color"> {
  imageUrl?: string;
  dimension?: number | string;
  applyMask?: boolean;
  imgColor?: string;
}

export const MaskedImageIcon: React.FC<ImageProps> = ({
  imageUrl,
  dimension = "50px",
  applyMask = true,
  imgColor,
  ...boxProps
}) => {
  return (
    <StyledBox
      role="img"
      style={
        applyMask
          ? {
              backgroundColor: imgColor,
              maskImage: `url(${imageUrl})`,
              WebkitMaskImage: `url(${imageUrl})`,
              width: dimension,
              height: dimension,
            }
          : {
              backgroundColor: "transparent",
              backgroundImage: `url(${imageUrl})`,
              width: dimension,
              height: dimension,
            }
      }
      {...boxProps}
    />
  );
};
