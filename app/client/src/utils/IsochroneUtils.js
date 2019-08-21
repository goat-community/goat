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
      const populationObj = feature.get("population")[0];
      const studyAreaName = Object.keys(populationObj)[0];
      const studyAreaNameReached = Object.keys(populationObj)[1];

      const obj = {
        isochrone: `${IsochroneUtils.getIsochroneAliasFromKey(
          feature.get("modus")
        )} - ${feature.get("step")} min`,
        studyArea: studyAreaName,
        population: populationObj[studyAreaName],
        reachPopulation: populationObj[studyAreaNameReached]
      };
      multiIsochroneTableData.push(obj);
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
  }
};

export default IsochroneUtils;
