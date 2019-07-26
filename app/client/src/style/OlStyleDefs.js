import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";
import OlCircle from "ol/style/Circle";
import OlIcon from "ol/style/Icon";

export default {
  boundaryStyle: () => {
    return new OlStyle({
      fill: new OlFill({
        color: [0, 0, 0, 0]
      }),
      stroke: new OlStroke({
        color: "#707070",
        width: 5.5
      })
    });
  },
  getMeasureStyle: measureConf => {
    return new OlStyle({
      fill: new OlFill({
        color: measureConf.fillColor || "rgba(255, 255, 255, 0.2)"
      }),
      stroke: new OlStroke({
        color: measureConf.strokeColor || "rgba(0, 0, 0, 0.5)",
        width: 4
      })
    });
  },
  getMeasureInteractionStyle: measureConf => {
    return new OlStyle({
      fill: new OlFill({
        color: measureConf.sketchFillColor || "rgba(255, 255, 255, 0.2)"
      }),
      stroke: new OlStroke({
        color: measureConf.sketchStrokeColor || "rgba(0, 0, 0, 0.5)",
        lineDash: [10, 10],
        width: 2
      }),
      image: new OlCircle({
        radius: 5,
        stroke: new OlStroke({
          color: measureConf.sketchVertexStrokeColor || "rgba(0, 0, 0, 0.7)"
        }),
        fill: new OlFill({
          color: measureConf.sketchVertexFillColor || "rgba(255, 255, 255, 0.2)"
        })
      })
    });
  },
  getSelectStyle: () => {
    return new OlStyle({
      fill: new OlFill({
        color: "rgba(255, 255, 255, 0.2)"
      }),
      stroke: new OlStroke({
        color: "rgba(0, 0, 0, 0.5)",
        width: 4
      })
    });
  },
  getIsochroneStyle: (styleData, addStyleInCache) => {
    const styleFunction = feature => {
      // Style array
      let styles = [];
      // Get the incomeLevel and modus from the feature properties
      let level = feature.get("step");
      let modus = feature.get("modus");
      let isVisible = feature.get("isVisible");
      let geomType = feature.getGeometry().getType();

      /**
       * Creates styles for isochrone polygon geometry type and isochrone
       * center marker.
       */
      if (
        geomType === "Polygon" ||
        geomType === "MultiPolygon" ||
        geomType === "LineString"
      ) {
        //Check feature isVisible Property
        if (isVisible === false) {
          return;
        }

        //Fallback isochrone style
        if (!modus) {
          if (!styleData.styleCache.default["GenericIsochroneStyle"]) {
            let genericIsochroneStyle = new OlStyle({
              fill: new OlFill({
                color: [0, 0, 0, 0]
              }),
              stroke: new OlStroke({
                color: "#0d0d0d",
                width: 7
              })
            });
            let payload = {
              style: genericIsochroneStyle,
              isochroneType: "default",
              styleName: "GenericIsochroneStyle"
            };
            addStyleInCache(payload);
          }
          styles.push(styleData.styleCache.default["GenericIsochroneStyle"]);
        }
        // If the modus is 1 it is a default isochrone
        if (modus === 1 || modus === 3) {
          if (!styleData.styleCache.default[level]) {
            let style = new OlStyle({
              stroke: new OlStroke({
                color: feature.get("color"),
                width: 5
              })
            });
            let payload = {
              style: style,
              isochroneType: "default",
              styleName: level
            };
            addStyleInCache(payload);
          }
          styles.push(styleData.styleCache.default[level]);
        } else {
          if (!styleData.styleCache.input[level]) {
            let style = new OlStyle({
              stroke: new OlStroke({
                color: feature.get("color"),
                width: 5
              })
            });
            let payload = {
              style: style,
              isochroneType: "input",
              styleName: level
            };
            addStyleInCache(payload);
          }
          styles.push(styleData.styleCache.input[level]);
        }
      } else {
        let path = `img/markers/marker-${feature.get("calculationNumber")}.png`;
        let markerStyle = new OlStyle({
          image: new OlIcon({
            anchor: [0.5, 0.96],
            src: path,
            scale: 0.5
          })
        });
        styles.push(markerStyle);
      }
      return styles;
    };

    return styleFunction;
  }
};
