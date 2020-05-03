import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";
import OlCircle from "ol/style/Circle";
import OlIcon from "ol/style/Icon";
import OlText from "ol/style/Text";

export function getMeasureStyle(measureConf) {
  return new OlStyle({
    fill: new OlFill({
      color: measureConf.fillColor || "rgba(255, 255, 255, 0.2)"
    }),
    stroke: new OlStroke({
      color: measureConf.strokeColor || "rgba(0, 0, 0, 0.5)",
      width: 4
    })
  });
}
export function getMeasureInteractionStyle(measureConf) {
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
}

export function getSelectStyle() {
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
}

export function getInfoStyle() {
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
}

export function getEditStyle() {
  return editStyleFn();
}

export function getIsochroneNetworkStyle() {
  const styleFunction = feature => {
    const color = feature.get("color");
    const style = new OlStyle({
      stroke: new OlStroke({
        color: color,
        width: 3
      })
    });
    return [style];
  };
  return styleFunction;
}
export function getIsochroneStyle(styleData, addStyleInCache) {
  const styleFunction = feature => {
    // Style array
    let styles = [];
    // Get the incomeLevel and modus from the feature properties
    let level = feature.get("step");
    let modus = feature.get("modus");
    let isVisible = feature.get("isVisible");
    let geomType = feature.getGeometry().getType();
    const color = feature.get("color");
    const highlightFeature = feature.get("highlightFeature");

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
      //highlight color
      if (highlightFeature !== false) {
        styles.push(
          new OlStyle({
            stroke: new OlStroke({
              color: "#FFFFFF",
              width: 8
            })
          })
        );
      }
      // If the modus is 1 it is a default isochrone
      if (modus === 1 || modus === 3) {
        if (
          !styleData.styleCache.default[level] ||
          styleData.styleCache.default[level].getStroke().getColor() !== color //Updates default cache when user has changed the color
        ) {
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
        if (
          !styleData.styleCache.input[level] ||
          styleData.styleCache.input[level].getStroke().getColor() !== color //Updates input cache when user has changed the color
        ) {
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
}

export function defaultStyle(feature) {
  const geomType = feature.getGeometry().getType();
  const style = new OlStyle({
    fill: new OlFill({
      color: ["MultiPolygon", "Polygon"].includes(geomType)
        ? "rgba(255, 0, 0, 0.7)"
        : [0, 0, 0, 0]
    }),
    stroke: new OlStroke({
      color: ["MultiPolygon", "Polygon"].includes(geomType)
        ? "#FF0000"
        : "#707070",
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
}

export function uploadedFeaturesStyle() {
  const style = new OlStyle({
    fill: new OlFill({
      color: "#2196F3"
    }),
    stroke: new OlStroke({
      color: "#2196F3",
      width: 3
    }),
    image: new OlCircle({
      radius: 7,
      fill: new OlFill({
        color: "#2196F3"
      })
    })
  });
  return [style];
}
export function waysModifiedStyle(feature) {
  const style = new OlStyle({
    fill: new OlFill({
      color: [0, 0, 0, 0]
    }),
    stroke: new OlStroke({
      color: "#FF0000",
      width: 3,
      lineDash: feature.getProperties()["status"] == 1 ? [0, 0] : [10, 10]
    }),
    image: new OlCircle({
      radius: 7,
      fill: new OlFill({
        color: "#FF0000"
      })
    })
  });
  return [style];
}
export function waysNewRoadStyle(feature) {
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
}
export function waysNewBridgeStyle(feature) {
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
}
export function editStyleFn() {
  const styleFunction = feature => {
    const props = feature.getProperties();
    if (feature.get("user_uploaded")) {
      return uploadedFeaturesStyle();
    }
    // Polygon (ex. building) style
    if (["MultiPolygon", "Polygon"].includes(feature.getGeometry().getType())) {
      return defaultStyle(feature);
    }

    // Linestring (ex. ways ) style
    if (
      (props.hasOwnProperty("way_type") && props["original_id"] == null) ||
      Object.keys(props).length == 1
    ) {
      //Distinguish Roads from Bridge features
      if (props.way_type == "bridge") {
        return waysNewBridgeStyle(feature);
      } else {
        return waysNewRoadStyle(feature);
      }
    } else if (props.hasOwnProperty("way_type")) {
      return waysModifiedStyle(feature); //Feature are modified
    } else {
      return defaultStyle(feature); //Features are from original table
    }
  };

  return styleFunction;
}

export function getFeatureHighlightStyle() {
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

export const baseStyleDefs = {
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
  }
};

/**
 * Mapillary styles
 */

export const mapillaryStyleDefs = {
  activeSequence: "",
  baseOverlayStyle: map => {
    const styleFunction = function(feature) {
      // console.log(feature);
      let color = "rgba(53, 175, 109,0.7)";
      if (
        feature.get("key") === mapillaryStyleDefs.activeSequence ||
        feature.get("skey") === mapillaryStyleDefs.activeSequence
      ) {
        color = "#30C2FF";
      }
      const styleConfig = {
        stroke: new OlStroke({
          color: color,
          width: 4
        })
      };
      if (map.getView().getZoom() > 17) {
        styleConfig.image = new OlCircle({
          radius: 6,
          fill: new OlFill({ color: color })
        });
      }
      const style = new OlStyle(styleConfig);
      return [style];
    };
    return styleFunction;
  },
  highlightStyle: feature => {
    let styles = [];
    const angle = feature.get("ca");
    const skey = feature.get("skey");
    if (angle) {
      const wifiStyle = new OlStyle({
        text: new OlText({
          text: "\ue1d8",
          scale: 1,
          font: '900 18px "Material Icons"',
          offsetY: -10,
          rotateWithView: true,
          rotation: (angle * Math.PI) / 180,
          fill: new OlFill({
            color:
              skey === mapillaryStyleDefs.activeSequence ? "#30C2FF" : "#047d50"
          }),
          stroke: new OlStroke({
            color:
              skey === mapillaryStyleDefs.activeSequence
                ? "#30C2FF"
                : "#047d50",
            width: 3
          })
        })
      });
      styles.push(wifiStyle);
    }
    const circleStyle = new OlStyle({
      text: new OlText({
        text: "\uf111",
        scale: 0.9,
        font: '900 18px "Font Awesome 5 Free"',
        fill: new OlFill({
          color:
            skey === mapillaryStyleDefs.activeSequence ? "#30C2FF" : "#047d50"
        }),
        stroke: new OlStroke({ color: "white", width: 4 })
      })
    });
    styles.push(circleStyle);
    return styles;
  },
  circleSolidStyle: new OlStyle({
    text: new OlText({
      text: "\uf111",
      scale: 0.7,
      font: '900 18px "Font Awesome 5 Free"',
      fill: new OlFill({ color: "red" }),
      stroke: new OlStroke({ color: "white", width: 4 })
    })
  }),
  wifiStyle: new OlStyle({
    text: new OlText({
      text: "\ue1d8",
      scale: 1.2,
      font: '900 18px "Material Icons"',
      offsetY: -10,
      rotation: 0,
      fill: new OlFill({ color: "red" }),
      stroke: new OlStroke({ color: "red", width: 3 })
    })
  }),
  updateBearingStyle: bearing => {
    const liveBearing = new OlStyle({
      text: new OlText({
        text: "\ue1d8",
        scale: 1.2,
        font: '900 18px "Material Icons"',
        offsetY: -10,
        rotateWithView: true,
        rotation: (bearing * Math.PI) / 180,
        fill: new OlFill({ color: "red" }),
        stroke: new OlStroke({ color: "red", width: 3 })
      })
    });
    return [liveBearing, mapillaryStyleDefs.circleSolidStyle];
  }
};
