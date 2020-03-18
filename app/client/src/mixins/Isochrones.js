/**
 * Mixin, which shares method between isochrone components.
 */
export const Isochrones = {
  methods: {
    deleteCalculation(calculation) {
      this.$refs.confirm
        .open(
          this.$t("isochrones.deleteTitle"),
          this.$t("isochrones.deleteMessage") + " " + calculation.id + " ?",
          { color: "green" }
        )
        .then(confirm => {
          if (confirm) {
            this.removeCalculation(calculation);
          }
        });
    }
  }
};
