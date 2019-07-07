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
        obj[modus][time] = pois !== null ? JSON.parse(pois) : null;
      });
    }
    return obj;
  }
};

export default IsochroneUtils;
