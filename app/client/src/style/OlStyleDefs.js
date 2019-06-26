import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";

export default {
  shopStyle: new OlStyle({
    stroke: new OlStroke({
      color: "red",
      width: 3.25
    })
  }),
  neWorldMvt: new OlStyle({
    stroke: new OlStroke({
      color: "gray",
      width: 1
    }),
    fill: new OlFill({
      color: "rgba(20,20,20,0.1)"
    })
  })
};
