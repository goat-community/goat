import {
  linearInterpolation,
  getClosest,
  interpolateColor
} from "../utils/Helpers";

/**
 * Util class for Isochrone Calculation
 */

const IsochroneUtils = {
  getCalculationFeatures: function getCalculationFeatures(
    calculation,
    IsochroneLayer
  ) {
    let data = calculation.data;
    let isochroneFeatures = [];
    if (data) {
      data.forEach(isochrone => {
        let id = isochrone.id;
        let feature = IsochroneLayer.getSource().getFeatureById(id);
        if (feature) {
          isochroneFeatures.push(feature);
        }
      });
    }

    return isochroneFeatures;
  },
  getCalculationPoisObject: function getCalculationPoisObject(
    isochroneFeatures
  ) {
    let obj = {};
    if (isochroneFeatures.length > 0) {
      isochroneFeatures.forEach(isochrone => {
        let modus = isochrone.get("modus");
        let time = isochrone.get("step");
        let pois = isochrone.get("sum_pois");
        if (!obj[modus]) {
          obj[modus] = {};
        }
        obj[modus][time] = pois;
      });
    }
    return obj;
  },
  getMultiIsochroneTableData: function getMultiIsochroneTableData(
    isochroneFeatures
  ) {
    let multiIsochroneTableData = [];
    isochroneFeatures.forEach(feature => {
      let obj = {
        isochrone: `${IsochroneUtils.getIsochroneAliasFromKey(
          feature.get("modus")
        )} - ${feature.get("step")} min`
      };
      const populationObj = feature.get("population");
      if (feature.get("population").bounding_box) {
        //Multi-isochrone is created using draw
        obj.studyArea = "-- (Draw)";
        obj.population = populationObj.bounding_box;
        obj.reachPopulation = populationObj.bounding_box_reached;
        multiIsochroneTableData.push(obj);
      } else {
        //Multi-isochrone is created from study-area

        populationObj.forEach(currentStudyArea => {
          multiIsochroneTableData.push(
            Object.assign(
              {
                studyArea: Object.keys(currentStudyArea)[0],
                population: currentStudyArea[Object.keys(currentStudyArea)[0]],
                reachPopulation:
                  currentStudyArea[Object.keys(currentStudyArea)[1]]
              },
              obj
            )
          );
        });
      }
    });
    return multiIsochroneTableData;
  },
  getIsochroneAliasFromKey: function getIsochroneAliasFromKey(key) {
    let isochroneMapping = {
      "1": "Default",
      "2": "Input",
      "3": "Default",
      "4": "Input"
    };
    let alias = isochroneMapping[key] ? isochroneMapping[key] : key;
    return alias;
  },
  getInterpolatedColor(lowestValue, highestValue, value, color) {
    const colorKeys = Object.keys(color).map(n => parseInt(n, 10));
    //====//
    // x1 lowest step value TODO: get this dynamically from the options
    // x2 highest step value  TODO: get this dynamically from the options
    // y1 lowest color key code
    // y2 highest color key code
    // x current step value
    // Interpolates step values down to color key length
    const interpolatedValue = linearInterpolation(
      lowestValue,
      highestValue,
      colorKeys[0],
      [...colorKeys].pop(),
      value // isochrone step or cost
    );
    let interpolatedColor;
    // Find if the interpolated value exists in colors key, if not find two closest values.
    if (colorKeys.includes(interpolatedValue)) {
      // No interpolation
      interpolatedColor = color[interpolatedValue];
    } else {
      // Interpolate using factor
      const closestKeys = getClosest(colorKeys, interpolatedValue); //ex [3,4] color object keys
      const lowerColor = color[closestKeys[0]];
      const upperColor = color[closestKeys[1]];
      const factor = interpolatedValue - closestKeys[0]; // factor goes from 0 => 1
      interpolatedColor = interpolateColor(lowerColor, upperColor, factor);
    }

    return interpolatedColor;
  }
};

export default IsochroneUtils;
