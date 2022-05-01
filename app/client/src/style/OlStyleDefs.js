import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";
import OlCircle from "ol/style/Circle";
import OlIcon from "ol/style/Icon";
import OlText from "ol/style/Text";
import OlFontSymbol from "../utils/FontSymbol";
import OlShadow from "../utils/Shadow";

import poisAoisStore from "../store/modules/poisaois";
import mapStore from "../store/modules/map";
import appStore from "../store/modules/app";
import { FA_DEFINITIONS } from "../utils/FontAwesomev6ProDefs";
import { getIconUnicode } from "../utils/Helpers";
import Point from "ol/geom/Point";
import { getArea } from "ol/sphere.js";
import i18n from "../../src/plugins/i18n";

OlFontSymbol.addDefs(
  {
    font: process.env.VUE_APP_FONTAWESOME_NPM_AUTH_TOKEN
      ? "'Font Awesome 6 Pro'"
      : "'Font Awesome 5 Free'",
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

export function getSearchHighlightStyle() {
  return [
    new OlStyle({
      fill: new OlFill({
        color: "rgba(255,0,0,0.2)"
      }),
      stroke: new OlStroke({
        color: "#FF0000",
        width: 3
      }),
      image: new OlCircle({
        radius: 8,
        stroke: new OlStroke({
          color: "#FF0000",
          width: 3
        }),
        fill: new OlFill({
          color: "rgba(255,0,0,0.2)"
        })
      })
    })
  ];
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

const routingIconUnicodes = {
  walking_standard: "fas fa-person-walking",
  walking_elderly: "fas fa-person-walking",
  walking_safe_night: "fas fa-person-walking",
  cycling_standard: "fas fa-bicycle",
  cycling_pedelec: "fas fa-bicycle",
  walking_wheelchair: "fas fa-wheelchair",
  walking_wheelchair_standard: "fas fa-wheelchair",
  walking_wheelchair_electric: "fas fa-wheelchair"
};

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
      if (feature.get("showLabel")) {
        if (geomType !== ["Polygon", "LineString"]) {
          styles.push(
            new OlStyle({
              geometry: feature => {
                const coordinates = feature
                  .getGeometry()
                  .getCoordinates()[0][0];
                let maxY = null;
                let index = null;
                // Find max coordinate Y
                coordinates.forEach(coordinate => {
                  if (maxY === null || coordinate[1] > maxY) {
                    maxY = coordinate[1];
                    index = coordinates.indexOf(coordinate);
                  }
                });
                const center = coordinates[index];
                return new Point(center);
              },
              text: new OlText({
                text: Math.round(feature.get("step") / 60) + " min",
                font: "bold 16px Arial",
                placement: "point",
                fill: new OlFill({
                  color: "white"
                }),
                maxAngle: 0,
                backgroundFill: new OlFill({
                  color: feature.get("color")
                }),
                padding: [2, 2, 2, 2]
              })
            })
          );
        } else {
          styles.push(
            new OlStyle({
              text: new OlText({
                text: Math.round(feature.get("step") / 60) + " min",
                font: "bold 16px Arial",
                placement: "line",
                fill: new OlFill({
                  color: feature.get("color")
                }),
                maxAngle: 0
              })
            })
          );
        }
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
      if (feature.get("showLabel") && feature.get("routing")) {
        let routingUnicode;
        if (routingIconUnicodes[feature.get("routing")]) {
          routingUnicode =
            FA_DEFINITIONS[routingIconUnicodes[feature.get("routing")]];
        } else {
          routingUnicode = feature.get("routing");
        }
        styles.push(
          new OlStyle({
            text: new OlText({
              text: `  ${feature.get("speed")} km/h`,
              font: "bold 14px Arial",
              scale: 1.2,
              textAlign: "left",
              placement: "point",
              fill: new OlFill({
                color: "white"
              }),
              maxAngle: 0,
              backgroundFill: new OlFill({
                color: "#800000"
              }),
              padding: [3, 3, 3, 3],
              offsetX: 38,
              offsetY: -27
            })
          }),
          new OlStyle({
            text: new OlText({
              text: `${routingUnicode}`,
              font: "16px FontAwesome",
              scale: 1.2,
              textAlign: "left",
              placement: "point",
              fill: new OlFill({
                color: "white"
              }),
              maxAngle: 0,
              backgroundFill: new OlFill({
                color: "#800000"
              }),
              padding: [3, 3, 3, 3],
              offsetX: 17,
              offsetY: -27
            })
          })
        );
      }
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
      ? "rgba(112, 112, 112, 0.5)"
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

const poisEditShadowStyleCache = {};

function poisEditShadowStyle(color, radius) {
  return new OlStyle({
    image: new OlShadow({
      radius: radius,
      blur: 5,
      offsetX: 0,
      offsetY: 0,
      fill: new OlFill({
        color: color
      })
    })
  });
}

const poisEditStyleCache = {};
export function poisEditStyle(feature) {
  const category = feature.get("category");
  if (
    !poisAoisStore.state.poisAois[category] ||
    ["MultiPolygon", "Polygon"].includes(feature.getGeometry().getType())
  ) {
    return [];
  }
  const calculationMode = appStore.state.calculationMode.active;
  if (calculationMode === "default" && feature.get("edit_type")) {
    return [];
  }

  if (calculationMode === "comparison" && !feature.get("edit_type")) {
    return [];
  }

  const poiIconConf = appStore.state.poiIcons[category];
  const editType = feature.get("edit_type");
  //edit_type m = modified, d = deleted, n = new
  const shadowColor = {
    n: "#6495ED",
    m: "#FFA500",
    d: "#FF0000"
  };
  var st = [];
  // Shadow Style for Editing POIs
  if (!editType) {
    st.push(poisEditShadowStyle("rgba(0,0,0,0.5)", 15));
  }
  if (!poisEditShadowStyleCache[editType]) {
    poisEditShadowStyleCache[editType] = poisEditShadowStyle(
      shadowColor[editType],
      25
    );
  }
  st.push(poisEditShadowStyleCache[editType]);
  // ----POIS-----

  let color = poiIconConf.color;
  if (editType === "d") {
    // Icon color for delete poi
    color = "#c9c9c9";
  }
  if (!poiIconConf || !poiIconConf.icon) {
    return [];
  }
  const icon = poiIconConf.icon;
  if (!poisEditStyleCache[icon + color]) {
    // Font style
    poisEditStyleCache[icon + color] = new OlStyle({
      image: new OlFontSymbol({
        form: "marker", //"none|circle|poi|bubble|marker|coma|shield|blazon|bookmark|hexagon|diamond|triangle|sign|ban|lozenge|square a form that will enclose the glyph, default none",
        gradient: false,
        glyph: icon,
        text: "", // text to use if no glyph is defined
        font: "sans-serif",
        fontSize: 0.7,
        fontStyle: "900",
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
  st.push(poisEditStyleCache[icon + color]);
  return st;
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
    if (props.layerName === "poi") {
      return poisEditStyle(feature);
    }
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
    if (feature.get("layerName") === "building" && feature.get("edit_type")) {
      const styles = [];
      const geomType = feature.getGeometry().getType();
      const strokeOpt = {
        color: ["MultiPolygon", "Polygon"].includes(geomType)
          ? "rgba(255, 0, 0, 1)"
          : "#707070",
        width: 3
      };
      const fillOpt = {
        color: ["MultiPolygon", "Polygon"].includes(geomType)
          ? "rgba(255, 0, 0, 0.5)"
          : [0, 0, 0, 0]
      };
      const properties = feature.getProperties();
      strokeOpt.lineDash = [0, 0];
      strokeOpt.width = 4;

      let isCompleted = true;
      let hasEntranceFeature = false;
      if (
        mapStore.state.reqFields &&
        mapStore.state.selectedEditLayer.get("name") === "building"
      ) {
        mapStore.state.reqFields.forEach(field => {
          if (!properties[field]) {
            isCompleted = false;
          }
        });
      }
      if (mapStore.state.bldEntranceLayer) {
        const extent = feature.getGeometry().getExtent();
        const entrancesInExtent = mapStore.state.bldEntranceLayer
          .getSource()
          .getFeaturesInExtent(extent);

        let countEntrances = 0;
        entrancesInExtent.forEach(entrance => {
          const buildingId = feature.get("id") || feature.getId();
          if (entrance.get("building_modified_id") === buildingId) {
            countEntrances += 1;
          }
        });
        countEntrances === 0
          ? (hasEntranceFeature = false)
          : (hasEntranceFeature = true);
      }

      if (isCompleted === true && hasEntranceFeature === true) {
        strokeOpt.color = "rgb(0,128,0, 0.7)";
        fillOpt.color = "rgb(0,128,0, 0.7)";
      }
      const area = getArea(feature.getGeometry());
      const building_levels = feature.get("building_levels") || 0;
      const population = feature.get("population");
      const area_label = i18n.t(
        "dynamicFields.attributes.building.labels.area"
      );
      const building_levels_label = i18n.t(
        "dynamicFields.attributes.building.labels.building_levels"
      );
      const population_label = i18n.t(
        "dynamicFields.attributes.building.labels.population"
      );
      const floor_area_label = i18n.t(
        "dynamicFields.attributes.building.labels.gross_floor_area"
      );
      // Add label for building.
      let fontSize = 11;

      if (
        resolution < 0.4 &&
        mapStore.state.editLayer &&
        mapStore.state.editLayer.get("showLabels") === 0
      ) {
        const style = new OlStyle({
          text: new OlText({
            text: `${area_label}: ${area.toFixed(
              0
            )} ㎡\n${building_levels_label}: ${building_levels}
            ${floor_area_label}: ${parseInt(area * building_levels)} ㎡
            ${population_label}: ${parseInt(population || 0)}`,
            overflow: true,
            font: `${fontSize}px Calibri, sans-serif`,
            fill: new OlFill({
              color: "black"
            }),
            backgroundFill: new OlFill({
              color: "orange"
            }),
            padding: [1, 1, 1, 1]
          })
        });
        styles.push(style);
      }
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

    if (feature.get("layerName") === "population") {
      return bldEntrancePointsStyle(feature, resolution);
    }

    return defaultStyle(feature, resolution);
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
    const styleFunction = feature => {
      // console.log(feature);
      let color = "rgba(53, 175, 109,0.7)";
      if (
        [
          feature.get("sequence"),
          feature.get("id"),
          feature.get("sequence_id")
        ].includes(mapillaryStyleDefs.activeSequence)
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
    const angle = feature.get("compass_angle");
    const skey = feature.get("sequence_id");
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
  if (!poiIconConf && !poiIconConf.color) return [];
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
        fontStyle: "900",
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
