import { Circle as CircleStyle, Fill, Stroke, Style } from "ol/style";
import OlStyleParser from "geostyler-openlayers-parser";
import { stylesRef } from "../style/OlStyleDefs";
export const OlStyleFactory = {
  /**
   * Returns an OpenLayers Style instance due to given config.
   *
   * @param  {Object} styleConf  Style config object
   * @return {Style}             OL Style instance
   */
  getInstance(styleConf) {
    if (!styleConf) {
      return;
    } else if (styleConf.radius) {
      return OlStyleFactory.createPointStyle(styleConf);
    } else if (styleConf.fillColor) {
      return OlStyleFactory.createPolygonStyle(styleConf);
    } else if (styleConf.strokeColor || styleConf.strokeWidth) {
      return OlStyleFactory.createLineStyle(styleConf);
    }
  },

  /**
   * Returns an OpenLayers style instance for point due to given config.
   *
   * @param  {Object} styleConf  Style config object
   * @return {Style}             OL style instance
   */
  createPointStyle(styleConf) {
    return new Style({
      image: new CircleStyle({
        radius: styleConf.radius,
        fill: OlStyleFactory.createFill(styleConf),
        stroke: OlStyleFactory.createStroke(styleConf)
      })
    });
  },

  /**
   * Returns an OpenLayers style instance for lines due to given config.
   *
   * @param  {Object} styleConf  Style config object
   * @return {Style}             OL style instance
   */
  createLineStyle(styleConf) {
    const olStyle = new Style({
      stroke: OlStyleFactory.createStroke(styleConf)
    });

    return olStyle;
  },

  /**
   * Returns an OpenLayers style instance for polygons due to given config.
   *
   * @param  {Object} styleConf  Style config object
   * @return {Style}             OL style instance
   */
  createPolygonStyle(styleConf) {
    let olStyle = OlStyleFactory.createLineStyle(styleConf);
    olStyle.setFill(OlStyleFactory.createFill(styleConf));

    return olStyle;
  },

  /**
   * Creates an OL Stroke object due to given config.
   *
   * @param  {Object} styleConf Style config object
   * @return {Stroke}           OL Stroke instance
   */
  createStroke(styleConf) {
    return new Stroke({
      color: styleConf.strokeColor,
      width: styleConf.strokeWidth
    });
  },

  /**
   * Creates an OL Fill object due to given config.
   *
   * @param  {Object} styleConf Style config object
   * @return {Fill}             OL Fill instance
   */
  createFill(styleConf) {
    return new Fill({
      color: styleConf.fillColor
    });
  },

  /**
   * Main function for rendering styles using geostyler parser.
   *
   * @param  {Object} styleObj Style config
   * @param  {String} layerName Layer name
   * @return {Style}             OL Style instance
   */
  getOlStyle(styleObj, layerName) {
    const styleFormat = styleObj.format;
    const styleConf = styleObj.style;
    let olStyle;
    switch (styleFormat) {
      case "geostyler": {
        styleObj.style.rules.forEach(rule => {
          //Set default filer if no filter is found for rule
          if (!rule.filter) {
            rule.filter = ["=="];
          }
          //Change Symbolizers outline color from rgba to hexa
          if (rule.symbolizers[0].outlineColor === "rgba(0, 0, 255, 0.0)") {
            rule.symbolizers[0].outlineColor = "#0000FF00";
          }
        });
        const parser = new OlStyleParser();
        olStyle = parser.writeStyle(styleConf);
        break;
      }
      case "custom": {
        olStyle = stylesRef[layerName];
        break;
      }
      default:
        break;
    }
    return olStyle;
  }
};
