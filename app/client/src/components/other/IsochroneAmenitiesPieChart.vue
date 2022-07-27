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
      this.selectedPoisOnlyKeys.forEach(amenity => {
        if (calculationData[amenity]) {
          datasets[0].data.push(
            calculationData[amenity][this.isochroneRange - 1]
          );
          datasets[0].backgroundColor.push(
            this.poisConfig[amenity].color[0] || "rgb(54, 162, 235)"
          );
          labels.push(
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
      calculationColors: "calculationColors"
    }),
    ...mapGetters("poisaois", {
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys"
    }),
    ...mapGetters("app", {
      poisConfig: "poisConfig"
    })
  }
};
</script>
