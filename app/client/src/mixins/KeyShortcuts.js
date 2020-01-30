/**
 * Mixin, which handles key shortcuts.
 */
export const KeyShortcuts = {
  methods: {
    addKeyupListener() {
      document.onkeyup = null;
      document.onkeyup = evt => {
        const key = evt.key;
        const code = evt.keyCode;
        if (key === "Escape" || code === "27") {
          if (this.clear) {
            this.clear();
          }
        }
      };
    },
    clear() {
      document.onkeyup = null;
    }
  }
};
