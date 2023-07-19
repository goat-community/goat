"use client";

import HeaderStack from "@/app/(dashboard)/content/HeaderStack";
import PreviewMap from "@/app/(dashboard)/content/PreviewMap";
import PreviewMenu from "@/app/(dashboard)/content/PreviewMenu";
import { makeStyles } from "@/lib/theme";

const useStyles = () =>
  makeStyles({ name: { ContentPage } })((theme) => ({
    root: {
      position: "relative",
      width: "100%",
      minHeight: "100vh",
      marginTop: "100px",
    },
    container: {
      padding: "18px 0",
      display: "flex",
      justifyContent: "space-between",
      gap: "16px",
      height: "732px",
    },
  }));

export default function ContentPage() {
  const { classes, cx } = useStyles()();
  // const theme = useTheme();

  const mapProps = {
    initialViewState: {
      longitude: 11.831704345197693,
      latitude: 48.124458667004006,
      zoom: 10,
      pitch: 0,
      bearing: 0,
      altitude: -1,
    },
    MAP_ACCESS_TOKEN:
      "pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA",
    mapStyle: "mapbox://styles/mapbox/streets-v11",
    scaleShow: false,
    navigationControl: false,
  };

  return (
    <div className={cx(classes.root)}>
      <HeaderStack className={cx(classes.header)} />
      <div className={cx(classes.container)}>
        <PreviewMenu />
        <PreviewMap {...mapProps} />
      </div>
    </div>
  );
}
