import { EventBus } from "../EventBus";

/**
 * Mixin, which binds the OL map to the target component.
 * Executes the onMapBound function of the target component, if available.
 */
export const Mapable = {
  created() {
    // if the OL map is not present in the vue prototype we have to wait until
    // it is mounted. Otherwise apply OL map as member var.
    if (!this.$map) {
      // apply OL map once OL map is mounted
      EventBus.$on("ol-map-mounted", olMap => {
        // make the OL map accesible in this component
        this.map = olMap;

        if (this.onMapBound) {
          this.onMapBound();
        }
      });
    } else {
      // OL map is already mounted --> directly apply as member
      this.map = this.$map;
      if (this.onMapBound) {
        this.onMapBound();
      }
    }
  }
};
