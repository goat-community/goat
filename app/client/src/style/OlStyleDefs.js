import OlStyle from "ol/style/Style";
import OlStroke from "ol/style/Stroke";
import OlFill from "ol/style/Fill";

export default {
  boundaryStyle: new OlStyle({
    fill: new OlFill({
      color: [0, 0, 0, 0]
    }),
    stroke: new OlStroke({
      color: "#707070",
      width: 5.5
    })
  })
};
