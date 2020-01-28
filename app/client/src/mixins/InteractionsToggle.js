import { EventBus } from "../EventBus";

/**
 * Mixin, which toggle interactions.
 */
export const InteractionsToggle = {
  created() {
    const me = this;
    EventBus.$on("ol-interaction-activated", activatedInteraction => {
      if (activatedInteraction !== me.interactionType) {
        //If a clear method does exist, call it.
        if (me.stop) {
          me.stop();
        }
      }
    });
  }
};
