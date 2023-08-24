import { Skeleton } from "@mui/material";
import { Fragment, useState } from "react";
interface Props {
  src: string;
  alt?: string;
  width?: number;
  height?: number;
  border?: "rectangular" | "rounded" | "circular";
  style?: React.CSSProperties;
}

export function SkeletonImage({ src, alt = "", width, height, border = "rectangular", style = {} }: Props) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const borderStyle = {
    rounded: { borderRadius: "4px" },
    circular: { borderRadius: "50%" },
    rectangular: {},
  };
  const imageStyle = imageLoaded ? borderStyle[border] : { display: "none" };

  const skeletonStyle = imageLoaded ? { display: "none" } : {};
  return (
    <Fragment>
      <Skeleton style={skeletonStyle} width={width} variant={border} height={height} />
      <img
        style={{ ...style, ...imageStyle }}
        src={src}
        alt={alt}
        width={width}
        height={height}
        onLoad={() => setImageLoaded(true)}
      />
    </Fragment>
  );
}
