import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";
import OlCircle from "ol/style/Circle";
import OlIcon from "ol/style/Icon";
import store from "../store/modules/isochrones";

const colorDiffDefault = [6.1, 13.42, 11.789];
const color1Default = [255, 255, 224];
const colorDiffInput = [1.789, 10.578, -9.631];
const color1Input = [34, 211, 41];

function setNetworkColor(time, colorDiff, color1) {
  let color;
  if (time < 1) {
    color = color1;
  } else {
    let diffTime = time - 1;
    color = [
      color1[0] - colorDiff[0] * diffTime,
      color1[1] - colorDiff[1] * diffTime,
      color1[2] - colorDiff[2] * diffTime
    ];
  }
  return color;
}

const OlStyleDefs = {
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
        color: [0, 0, 0, 0]
      }),
      stroke: new OlStroke({
        color: "#fe4a49",
        width: 5,
        lineDash: [10, 10]
      }),
      image: new OlCircle({
        radius: 7,
        fill: new OlFill({
          color: "#FF0000"
        })
      })
    });
  },
  getInfoStyle: () => {
    return new OlStyle({
      fill: new OlFill({
        color: "rgba(255,0,0, 0.2)"
      }),
      stroke: new OlStroke({
        color: "#FF0000",
        width: 2
      }),
      image: new OlCircle({
        radius: 7,
        fill: new OlFill({
          color: "#FF0000"
        })
      })
    });
  },
  getEditStyle: () => {
    //TODO: Add a generic style here for other layers
    return OlStyleDefs.waysStyleFn();
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
              fill: new OlFill({
                color: [0, 0, 0, 0]
              }),
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
              fill: new OlFill({
                color: [0, 0, 0, 0]
              }),
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
  },
  getIsochroneNetworkStyle: () => {
    const styleFunction = feature => {
      const modus = feature.get("modus");
      const level = feature.get("cost");
      let speed = store.state.options.speed * 16.6666667;
      let color;
      if (modus == 1 || modus == 3) {
        color = setNetworkColor(level / speed, colorDiffDefault, color1Default);
      } //If the parent_id is not one it is a input isochrone
      else {
        color = setNetworkColor(level / speed, colorDiffInput, color1Input);
      }

      const style = new OlStyle({
        stroke: new OlStroke({
          color: `rgb(${Math.round(color[0])},${Math.round(
            color[1]
          )},${Math.round(color[2])})`,
          width: 3
        })
      });

      return [style];
    };
    return styleFunction;
  },
  defaultStyle: () => {
    const style = new OlStyle({
      fill: new OlFill({
        color: [0, 0, 0, 0]
      }),
      stroke: new OlStroke({
        color: "#707070",
        width: 3
      }),
      image: new OlCircle({
        radius: 7,
        fill: new OlFill({
          color: "#FF0000"
        })
      })
    });
    return [style];
  },
  waysModifiedStyle: feature => {
    const style = new OlStyle({
      fill: new OlFill({
        color: [0, 0, 0, 0]
      }),
      stroke: new OlStroke({
        color: "#FF0000",
        width: 3,
        lineDash: feature.getProperties()["status"] == 1 ? [0, 0] : [10, 10]
      })
    });
    return [style];
  },
  waysNewRoadStyle: feature => {
    const style = new OlStyle({
      fill: new OlFill({
        color: [0, 0, 0, 0]
      }),
      stroke: new OlStroke({
        color: "#6495ED",
        width: 4,
        lineDash: feature.getProperties()["status"] == 1 ? [0, 0] : [10, 10]
      })
    });
    return [style];
  },
  waysNewBridgeStyle: feature => {
    const style = new OlStyle({
      fill: new OlFill({
        color: [0, 0, 0, 0]
      }),
      stroke: new OlStroke({
        color: "#FFA500",
        width: 4,
        lineDash: feature.getProperties()["status"] == 1 ? [0, 0] : [10, 10]
      })
    });
    return [style];
  },
  waysStyleFn: () => {
    const me = OlStyleDefs;
    const styleFunction = feature => {
      const props = feature.getProperties();
      if (
        (props.hasOwnProperty("type") && props["original_id"] == null) ||
        Object.keys(props).length == 1
      ) {
        //Distinguish Roads from Bridge features
        if (props.type == "bridge") {
          return me.waysNewBridgeStyle(feature);
        } else {
          return me.waysNewRoadStyle(feature);
        }
      } else if (
        !props.hasOwnProperty("original_id") &&
        Object.keys(props).length > 1
      ) {
        return me.defaultStyle(); //Features are from original table
      } else {
        return me.waysModifiedStyle(feature); //Feature are modified
      }
    };

    return styleFunction;
  },
  getFeatureHighlightStyle: () => {
    return [
      new OlStyle({
        fill: new OlFill({
          color: [0, 0, 0, 0]
        }),
        stroke: new OlStroke({
          color: "#FF0000",
          width: 10
        }),
        image: new OlCircle({
          radius: 10,
          fill: new OlFill({
            color: "#FF0000"
          })
        })
      })
    ];
  }
};

export default OlStyleDefs;
