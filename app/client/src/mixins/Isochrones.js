/**
 * Mixin, which shares method between isochrone components.
 */
export const Isochrones = {
  methods: {
    /**
     * Isochrone delete calculation method.
     */
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
    },
    /**
     * CanCalculate checks if the user is allowed to calulate scenario isochrones or not
     */
    canCalculateScenario(selectedCalcMode) {
      if (!this.scenarioDataTable || !this.toggleSnackbar) {
        return;
      }
      const scenarioOptions = ["scenario", "comparison"];
      let areAllFeaturesUploaded = true;
      this.scenarioDataTable.forEach(f => {
        if (f.status !== "Uploaded") {
          areAllFeaturesUploaded = false;
        }
      });
      if (
        this.scenarioDataTable.length === 0 &&
        scenarioOptions.includes(selectedCalcMode)
      ) {
        //Show snackbar warning that user has features not yet uploaded
        this.toggleSnackbar({
          type: "warning", //success or error
          message: "noScenarioFeatureChangeAvailable",
          state: true,
          timeout: 150000
        });
        return;
      }
      if (
        this.scenarioDataTable.length > 0 &&
        areAllFeaturesUploaded === false &&
        scenarioOptions.includes(selectedCalcMode)
      ) {
        //Show snackbar warning that user has features not yet uploaded
        this.toggleSnackbar({
          type: "warning", //success or error
          message: "notAllScnearioFeaturesUploaded",
          state: true,
          timeout: 150000
        });
      } else {
        //Hide snackbar.
        this.toggleSnackbar({
          state: false
        });
      }
    }
  }
};
