<script>
import { Pie } from "vue-chartjs";
import { mapGetters } from "vuex";
import { EventBus } from "../../EventBus";

export default {
  extends: Pie,
  props: ["calculationIndex"],
  mounted() {
    this.renderPieChart();
    EventBus.$on("ol-interaction-activated", interaction => {
      if (interaction === "languageChange") {
        this.renderPieChart();
      }
    });
  },
  methods: {
    renderPieChart: function() {
      const labels = [];
      const datasets = [
        {
          borderWidth: 1,
          backgroundColor: [],
          data: []
        }
      ];
      const calculation = this.selectedCalculations[this.calculationIndex];
      const calculationData = calculation.surfaceData.accessibility;
      // Add only amenities
      let keys = [];
      let config = [];
      if (this.chartDatasetType === 1) {
        keys = [...this.selectedPoisOnlyKeys].reverse();
        config = this.poisConfig;
      } else if (this.chartDatasetType === 2) {
        keys = [...this.selectedAoisOnlyKeys].reverse();
        config = this.aoisConfig;
      }
      keys.forEach(amenity => {
        if (calculationData[amenity]) {
          datasets[0].data.unshift(
            calculationData[amenity][this.isochroneRange - 1]
          );
          datasets[0].backgroundColor.unshift(
            config[amenity].color[0] || "rgb(54, 162, 235)"
          );
          labels.unshift(
            this.$te(`pois.${amenity}`) ? this.$t(`pois.${amenity}`) : amenity
          );
        }
      });

      this.renderChart(
        {
          labels,
          datasets
        },
        {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 0
          }
        }
      );
    }
  },
  watch: {
    selectedPoisOnlyKeys: {
      handler: function() {
        this.renderPieChart();
      },
      deep: true
    },
    selectedAoisOnlyKeys: {
      handler: function() {
        this.renderPieChart();
      },
      deep: true
    },
    isochroneRange: function() {
      this.renderPieChart();
    },
    chartDatasetType: function() {
      this.renderPieChart();
    },
    selectedCalculations() {
      this.renderPieChart();
    }
  },
  computed: {
    ...mapGetters("isochrones", {
      selectedCalculations: "selectedCalculations",
      isochroneRange: "isochroneRange",
      chartDatasetType: "chartDatasetType",
      preDefCalculationColors: "preDefCalculationColors"
    }),
    ...mapGetters("poisaois", {
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys",
      selectedAoisOnlyKeys: "selectedAoisOnlyKeys"
    }),
    ...mapGetters("app", {
      poisConfig: "poisConfig",
      aoisConfig: "aoisConfig"
    })
  }
};
</script>
