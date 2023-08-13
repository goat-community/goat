// import { makeStyles } from "@/lib/theme";
// import { useMemo } from "react";

// export type DatasetAttribution = {
//   title: string;
//   url: string;
// };

// const MapboxLogo = () => {
//   const { classes } = useStyles();
//   return (
//     <div className={classes.attributeLogo}>
//       Basemap by:
//       <a
//         className={classes.mapboxCtrlLogo}
//         target="_blank"
//         rel="noopener noreferrer"
//         href="https://www.mapbox.com/"
//         aria-label="Mapbox logo"
//       />
//     </div>
//   );
// };

// const DatasetAttributions = ({ datasetAttributions }: { datasetAttributions: DatasetAttribution[] }) => {
//   const { classes } = useStyles();
//   return (
//     <>
//       {datasetAttributions?.length ? (
//         <div className={classes.datasetAttributionsContainer}>
//           {datasetAttributions.map((ds, idx) => (
//             <a href={ds.url} target="_blank" rel="noopener noreferrer" key={`${ds.title}_${idx}`}>
//               {ds.title}
//               {idx !== datasetAttributions.length - 1 ? ", " : null}
//             </a>
//           ))}
//         </div>
//       ) : null}
//     </>
//   );
// };

export default function Attribution({
  basemapLogo = "",
  showOsmBasemapAttribution = false,
  datasetAttributions,
}: {
  basemapLogo?: string;
  showOsmBasemapAttribution?: boolean;
  datasetAttributions: DatasetAttribution[];
}) {
  const { classes } = useStyles();

  return (
    // <div className={classes.attribution}>
    //   <div className={classes.endHorizontalFlexbox}>
    //     <DatasetAttributions datasetAttributions={datasetAttributions} />
    //     <div className={classes.attritionLink}>
    //       {datasetAttributions?.length ? <span className={classes.pipeSeparator}>|</span> : null}
    //       <a href="https://www.mapbox.com/about/maps/" target="_blank" rel="noopener noreferrer">
    //         © Mapbox |{" "}
    //       </a>
    //       <a href="https://www.mapbox.com/map-feedback/" target="_blank" rel="noopener noreferrer">
    //         <strong>Improve this map </strong>
    //         <strong> | </strong>
    //       </a>
    //       <MapboxLogo />
    //     </div>
    //   </div>
    // </div>
  );
}

// const useStyles = makeStyles()((theme) => ({
//   datasetAttributionsContainer: {
//     maxWidth: "180px",
//     textOverflow: "ellipsis",
//     whiteSpace: "nowrap",
//     overflow: "hidden",
//     color: "#6A7485",
//     marginRight: "2px",
//     lineHeight: "1.4em",
//     "&:hover": {
//       whiteSpace: "inherit",
//     },
//   },
//   attributeLogo: {
//     display: "flex",
//     fontSize: "10px",
//     justifyContent: "flex-end",
//     alignItems: "center",
//     color: "#6A7485",
//   },
//   mapboxCtrlLogo: {
//     width: "72px",
//     marginLeft: "4px",
//     backgroundSize: "contain",
//   },
//   attribution: {
//     bottom: 0,
//     right: 0,
//     position: "absolute",
//     display: "block",
//     margin: "0 10px 6px",
//     zIndex: 1,
//   },
//   endHorizontalFlexbox: {
//     display: "flex",
//     flexDirection: "row",
//     alignItems: "end",
//   },
//   attritionLink: {
//     display: "flex",
//     alignItems: "center",
//     marginLeft: "10px",
//   },
//   pipeSeparator: {
//     fontSize: "10px",
//   }
// }));

