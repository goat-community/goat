<template>
  <div></div
></template>

<script>
// helper function to detect a CSS color
// Taken from Vuetify sources
// https://github.com/vuetifyjs/vuetify/blob/master/packages/vuetify/src/mixins/colorable.ts
function isCssColor(color) {
  return !!color && !!color.match(/^(#|(rgb|hsl)a?\()/);
}

import Vue from "vue";
import Map from "ol/Map";
import View from "ol/View";
import Zoom from "ol/control/Zoom";
import SelectInteraction from "ol/interaction/Select";
import { defaults as defaultInteractions } from "ol/interaction";
import Overlay from "ol/Overlay";
// import the app-wide EventBus
import { EventBus } from "../../EventBus";
import { LayerFactory } from "../../factory/layer.js";

export default {
  name: "app-map",
  props: {
    color: { type: String, required: false, default: "green darken-3" }
  },
  data() {
    return {
      zoom: this.$appConfig.map.zoom,
      center: this.$appConfig.map.center
    };
  },
  mounted() {
    var me = this;
    // Make the OL map accessible for Mapable mixin even 'ol-map-mounted' has
    // already been fired. Don not use directly in cmps, use Mapable instead.
    Vue.prototype.$map = me.map;
    // Send the event 'ol-map-mounted' with the OL map as payload
    EventBus.$emit("ol-map-mounted", me.map);

    // resize the map, so it fits to parent
    window.setTimeout(() => {
      me.map.setTarget(document.getElementById("ol-map-container"));
      me.map.updateSize();

      // adjust the bg color of the OL buttons (like zoom, rotate north, ...)
      me.setOlButtonColor();

      // initialize map hover functionality
      me.setupMapHover();
    }, 200);
  },
  created() {
    var me = this;

    // make map rotateable according to property
    const interactions = defaultInteractions({
      altShiftDragRotate: me.rotateableMap
    });
    let controls = [new Zoom()];
    me.map = new Map({
      layers: [],
      controls: controls,
      interactions: interactions,
      view: new View({
        center: me.center || [0, 0],
        zoom: me.zoom
      })
    });

    // create layers from config and add them to map
    const layers = me.createLayers();
    me.map.getLayers().extend(layers);
  },

  methods: {
    /**
     * Creates the OL layers due to the map "layers" array in app config.
     * @return {ol.layer.Base[]} Array of OL layer instances
     */
    createLayers() {
      const me = this;
      let layers = [];
      this.$appConfig.map.layers.reverse().forEach(function(lConf) {
        let layer = LayerFactory.getInstance(lConf);
        layers.push(layer);

        // if layer is selectable register a select interaction
        if (lConf.selectable) {
          const selectClick = new SelectInteraction({
            layers: [layer]
          });
          // forward an event if feature selection changes
          selectClick.on("select", function(evt) {
            // TODO use identifier for layer (once its implemented)
            EventBus.$emit(
              "map-selectionchange",
              layer.get("name"),
              evt.selected,
              evt.deselected
            );
          });
          // register/activate interaction on map
          me.map.addInteraction(selectClick);
        }
      });

      return layers;
    },

    /**
     * Sets the background color of the OL buttons to the color property.
     */
    setOlButtonColor() {
      var me = this;

      if (isCssColor(me.color)) {
        // directly apply the given CSS color
        if (document.querySelector(".ol-zoom")) {
          document.querySelector(".ol-zoom .ol-zoom-in").style.backgroundColor =
            me.color;
          document.querySelector(
            ".ol-zoom .ol-zoom-out"
          ).style.backgroundColor = me.color;
        }
        if (document.querySelector(".ol-rotate")) {
          document.querySelector(
            ".ol-rotate .ol-rotate-reset"
          ).style.backgroundColor = me.color;
        }
      } else {
        // apply vuetify color by transforming the color to the corresponding
        // CSS class (see https://vuetifyjs.com/en/framework/colors)
        const [colorName, colorModifier] = me.color
          .toString()
          .trim()
          .split(" ", 2);
        if (document.querySelector(".ol-zoom")) {
          document
            .querySelector(".ol-zoom .ol-zoom-in")
            .classList.add(colorName);
          document
            .querySelector(".ol-zoom .ol-zoom-in")
            .classList.add(colorModifier);
          document
            .querySelector(".ol-zoom .ol-zoom-out")
            .classList.add(colorName);
          document
            .querySelector(".ol-zoom .ol-zoom-out")
            .classList.add(colorModifier);
        }
        if (document.querySelector(".ol-rotate")) {
          document
            .querySelector(".ol-rotate .ol-rotate-reset")
            .classList.add(colorName);
          document
            .querySelector(".ol-rotate .ol-rotate-reset")
            .classList.add(colorModifier);
        }
      }
    },
    /**
     * Initializes the map hover functionality:
     * Adds a little tooltip like DOM element, wrapped as OL Overlay to the
     * map.
     * Registers a 'pointermove' event on the map and shwos the layer's
     * 'hoverAttribute' if the layer is configured as 'hoverable'
     */
    setupMapHover() {
      const me = this;
      const map = me.map;
      let overlay;
      let overlayEl;

      // create a span to show map tooltip
      overlayEl = document.createElement("span");
      overlayEl.classList.add("wg-hover-tooltiptext");
      map.getTarget().append(overlayEl);

      // wrap the tooltip span in a OL overlay and add it to map
      overlay = new Overlay({
        element: overlayEl,
        autoPan: true,
        autoPanAnimation: {
          duration: 250
        }
      });
      map.addOverlay(overlay);

      map.on("pointermove", function(event) {
        let hoverAttr;
        const features = map.getFeaturesAtPixel(event.pixel, {
          layerFilter: layer => {
            if (layer.get("hoverable")) {
              hoverAttr = layer.get("hoverAttribute");
            }
            return layer.get("hoverable");
          }
        });
        if (!features || !hoverAttr) {
          hoverAttr = null;
          overlayEl.innerHTML = null;
          overlay.setPosition(undefined);
          return;
        }
        const feature = features[0];
        var attr = feature.get(hoverAttr);
        overlayEl.innerHTML = attr;
        overlay.setPosition(event.coordinate);
      });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
div.ol-zoom {
  top: auto;
  left: auto;
  bottom: 3em;
  right: 0.5em;
}

div.ol-attribution.ol-uncollapsible {
  bottom: 12px;
}

/* Hover tooltip */
.wg-hover-tooltiptext {
  width: 120px;
  background-color: rgba(211, 211, 211, 0.9);
  color: #222;
  text-align: center;
  padding: 5px;
  border-radius: 6px;

  /* Position the hover tooltip */
  position: absolute;
  z-index: 1;
}
</style>
