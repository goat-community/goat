import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";
import OlCircle from "ol/style/Circle";
import OlIcon from "ol/style/Icon";
import OlText from "ol/style/Text";
import OlFontSymbol from "../utils/FontSymbol";
import OlShadow from "../utils/Shadow";

import poisAoisStore from "../store/modules/poisaois";
import appStore from "../store/modules/app";
import { FA_DEFINITIONS } from "../utils/FontAwesomev6ProDefs";
import { getIconUnicode } from "../utils/Helpers";

OlFontSymbol.addDefs(
  {
    font: "FontAwesome",
    name: "FontAwesome",
    prefix: ""
  },
  FA_DEFINITIONS
);

const CUSTOM_FA_DEFS = {};
if (window.FontAwesomeKitConfig && window.FontAwesomeKitConfig.iconUploads) {
  const iconNames = Object.keys(window.FontAwesomeKitConfig.iconUploads);
  iconNames.forEach(iconName => {
    const unicode = window.FontAwesomeKitConfig.iconUploads[iconName].u;
    if (unicode) {
      CUSTOM_FA_DEFS[`fak fa-${iconName}`] = getIconUnicode(
        `fak fa-${iconName}`
      );
    }
  });
}

OlFontSymbol.addDefs(
  {
    font: "Font Awesome Kit",
    name: "Font Awesome Kit",
    prefix: ""
  },
  CUSTOM_FA_DEFS
);

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

export function studyAreaStyle() {
  return new OlStyle({
    fill: new OlFill({
      color: "rgba(96, 96, 98, 0.7)"
    }),
    stroke: new OlStroke({
      color: "#606062",
      width: 5
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

export function getIsochroneStyle() {
  const styleFunction = feature => {
    // Style array
    let styles = [];
    // Get the incomeLevel and modus from the feature properties
    let modus = feature.get("modus");
    let isVisible = feature.get("isVisible");
    let geomType = feature.getGeometry().getType();
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
        let genericIsochroneStyle = new OlStyle({
          fill: new OlFill({
            color: [0, 0, 0, 0]
          }),
          stroke: new OlStroke({
            color: "#0d0d0d",
            width: 7
          })
        });

        styles.push(genericIsochroneStyle);
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
      if (modus === "default" || modus === "comparison") {
        let style = new OlStyle({
          fill: new OlFill({
            color: [0, 0, 0, 0]
          }),
          stroke: new OlStroke({
            color: feature.get("color"),
            width: 5
          })
        });

        styles.push(style);
      } else {
        let style = new OlStyle({
          fill: new OlFill({
            color: [0, 0, 0, 0]
          }),
          stroke: new OlStroke({
            color: feature.get("color"),
            width: 5
          })
        });

        styles.push(style);
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
  const styles = [];
  const geomType = feature.getGeometry().getType();
  const strokeOpt = {
    color: ["MultiPolygon", "Polygon"].includes(geomType)
      ? "#707070"
      : "#707070",
    width: 3
  };
  const fillOpt = {
    color: ["MultiPolygon", "Polygon"].includes(geomType)
      ? "#707070"
      : [0, 0, 0, 0]
  };
  const style = new OlStyle({
    fill: new OlFill(fillOpt),
    stroke: new OlStroke(strokeOpt),
    image: new OlCircle({
      radius: 7,
      fill: new OlFill({
        color: "#707070"
      })
    })
  });
  styles.push(style);
  return styles;
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
export function waysNewRoadStyle() {
  const style = new OlStyle({
    stroke: new OlStroke({
      color: "#6495ED",
      width: 4
    })
  });
  return [style];
}

export function waysNewBridgeStyle() {
  const style = new OlStyle({
    stroke: new OlStroke({
      color: "#FFA500",
      width: 4
    })
  });
  return [style];
}

export function buildingStyleWithPopulation() {
  return new OlStyle({
    fill: new OlFill({
      color: "rgb(0,128,0, 0.7)"
    })
  });
}
export function buildingStyleWithNoPopulation() {
  return new OlStyle({
    fill: new OlFill({
      color: "#FF0000"
    })
  });
}

export function deletedStyle() {
  const style = new OlStyle({
    stroke: new OlStroke({
      color: "#FF0000",
      width: 4,
      lineDash: [5, 5]
    })
  });
  return [style];
}

export function editStyleFn() {
  const styleFunction = (feature, resolution) => {
    const props = feature.getProperties();
    // Deleted Style
    if (props.edit_type === "d") {
      return deletedStyle();
    }

    // New road Style
    if (feature.get("layerName") === "way") {
      if (props.way_type == "bridge") {
        return waysNewBridgeStyle();
      } else if (props.way_type == "road") {
        return waysNewRoadStyle();
      }
    }
    if (props.layerName === "building" && props.hasOwnProperty("edit_type")) {
      if (
        (props.building_type === "residential" && props.population) ||
        props.building_type !== "residential"
      ) {
        return buildingStyleWithPopulation();
      } else {
        return buildingStyleWithNoPopulation();
      }
    }

    if (feature.get("layerName") === "population") {
      return bldEntrancePointsStyle(feature, resolution);
    }

    return defaultStyle(feature);
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

export function isochroneOverlayStyle(feature) {
  if (feature.get("isVisible") === false) {
    return [];
  } else {
    return [
      new OlStyle({
        fill: new OlFill({
          color: "rgba(255, 0, 0, 0.3)"
        }),
        stroke: new OlStroke({
          color: "#FF0000",
          width: 3
        }),
        image: new OlCircle({
          radius: 5,
          fill: new OlFill({
            color: "#FF0000"
          })
        })
      })
    ];
  }
}

export function studyAreaASelectStyle() {
  return [
    new OlStyle({
      fill: new OlFill({
        color: "rgba(255, 0, 0, 0.5)"
      }),
      stroke: new OlStroke({
        color: "#FF0000",
        width: 5,
        lineDash: [10, 10]
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

export function bldEntrancePointsStyle(feature, resolution) {
  let radius = 8;
  if (resolution > 4) {
    return [];
  }
  const styles = [];
  styles.push(
    new OlStyle({
      fill: new OlFill({
        color: "#800080"
      }),
      stroke: new OlStroke({
        color: "#800080",
        width: radius
      }),
      image: new OlCircle({
        radius: radius,
        fill: new OlFill({
          color: "#800080"
        })
      })
    })
  );
  return styles;
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
  },
  subStudyAreaStyle: () => {
    return new OlStyle({
      fill: new OlFill({
        color: "rgba(127,127,191,0.3)"
      }),
      stroke: new OlStroke({
        color: "rgba(127,127,191)",
        width: 2
      })
    });
  }
};

/**
 * Mapillary styles -
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
/**
 * PoisAois layer style ---------------------
 */
const poisAoisStyleCache = {};
const poisShadowStyle = new OlStyle({
  image: new OlShadow({
    radius: 15,
    blur: 5,
    offsetX: 0,
    offsetY: 0,
    fill: new OlFill({
      color: "rgba(0,0,0,0.5)"
    })
  })
});

export function poisAoisStyle(feature) {
  const category = feature.get("category");
  if (!poisAoisStore.state.poisAois[category]) {
    return [];
  }
  const poiIconConf = appStore.state.poiIcons[category];
  const color = poiIconConf.color;

  var st = [];
  // ----AOIS-----
  if (["MultiPolygon", "Polygon"].includes(feature.getGeometry().getType())) {
    if (!poisAoisStyleCache[category + color]) {
      poisAoisStyleCache[category + color] = new OlStyle({
        fill: new OlFill({
          color: color
        }),
        stroke: new OlStroke({
          color: color,
          width: 1
        })
      });
    }
    st.push(poisAoisStyleCache[category + color]);
    return st;
  }
  // ----POIS-----
  // Shadow style
  st.push(poisShadowStyle);
  if (!poiIconConf || !poiIconConf.icon) {
    return [];
  }
  const icon = poiIconConf.icon;
  if (!poisAoisStyleCache[icon + color]) {
    // Font style
    poisAoisStyleCache[icon + color] = new OlStyle({
      image: new OlFontSymbol({
        form: "marker", //"none|circle|poi|bubble|marker|coma|shield|blazon|bookmark|hexagon|diamond|triangle|sign|ban|lozenge|square a form that will enclose the glyph, default none",
        gradient: false,
        glyph: icon,
        text: "", // text to use if no glyph is defined
        font: "sans-serif",
        fontSize: 0.7,
        radius: 20,
        rotation: 0,
        rotateWithView: false,
        offsetY: -20,
        color: color, // icon color
        fill: new OlFill({
          color: "#fff" // marker color
        }),
        stroke: new OlStroke({
          color: color,
          width: 2
        })
      }),
      stroke: new OlStroke({
        width: 2,
        color: "#f80"
      }),
      fill: new OlFill({
        color: [255, 136, 0, 0.6]
      })
    });
  }
  st.push(poisAoisStyleCache[icon + color]);
  return st;
}

export const stylesRef = {
  poisAoisStyle: poisAoisStyle,
  study_area_crop: baseStyleDefs.boundaryStyle,
  sub_study_area: baseStyleDefs.subStudyAreaStyle
};
