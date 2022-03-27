import {
  linearInterpolation,
  getClosest,
  interpolateColor
} from "../utils/Helpers";
import i18n from "../../src/plugins/i18n";
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
        let pois = isochrone.get("reached_opportunities");
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
        )} - ${Math.round(feature.get("step") / 60)} min`
      };
      const populationObj = feature.get("reached_opportunities");
      if (
        feature.get("reached_opportunities").name ||
        feature.get("reached_opportunities").name == "polygon"
      ) {
        //Multi-isochrone is created using draw
        obj.studyArea = "-- (Draw)";
        obj.population = populationObj.total_population;
        obj.reachPopulation = populationObj.reached_population;

        obj.shared =
          obj.population == 0 || obj.reachPopulation == 0
            ? "-"
            : `${((obj.reachPopulation / obj.population) * 100).toFixed(1)}%`;

        multiIsochroneTableData.push(obj);
      } else {
        //Multi-isochrone is created from study-area

        Object.keys(populationObj).forEach(currentStudyAreaKey => {
          const currentStudyArea = populationObj[currentStudyAreaKey];
          const _obj = {
            studyArea: currentStudyArea.name,
            population: currentStudyArea.total_population,
            reachPopulation: currentStudyArea.reached_population
          };
          if (_obj.population && _obj.reachPopulation) {
            _obj.shared = `${(
              (_obj.reachPopulation / _obj.population) *
              100
            ).toFixed(1)}%`;
          }
          multiIsochroneTableData.push(Object.assign(_obj, obj));
        });
      }
    });
    return multiIsochroneTableData;
  },
  getIsochroneAliasFromKey(key) {
    let alias = key ? i18n.t(`isochrones.mode.${key.toLowerCase()}`) : key;
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
