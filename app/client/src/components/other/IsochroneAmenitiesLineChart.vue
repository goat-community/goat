<script>
import { Line } from "vue-chartjs";
import { mapGetters } from "vuex";
import { EventBus } from "../../EventBus";

import annotationPlugin from "chartjs-plugin-annotation";
// import zoomPlugin from "chartjs-plugin-zoom";
export default {
  extends: Line,
  mounted() {
    this.addPlugin(annotationPlugin);
    // this.addPlugin(zoomPlugin);
    this.renderLineChart();
    EventBus.$on("ol-interaction-activated", interaction => {
      if (interaction === "languageChange") {
        this.renderLineChart();
      }
    });
  },
  methods: {
    renderLineChart: function() {
      const accessibilityData = this.selectedCalculations[0].surfaceData
        .accessibility;
      const accessibilityKeys = Object.keys(accessibilityData);
      const labels = [...accessibilityData[accessibilityKeys[0]].keys()];
      const datasets = [];
      this.selectedCalculations.forEach((calculation, index) => {
        const calculationData = calculation.surfaceData.accessibility;
        if (this.chartDatasetType === 0) {
          // add only population data
          datasets.push({
            data: calculationData["population"],
            label: this.$te(`pois.population`)
              ? this.$t(`pois.population`)
              : "population",
            fill: false,
            borderColor: this.calculationColors[index],
            borderDash: index === 0 ? [0, 0] : [10, 5],
            pointRadius: 1
          });
        } else {
          let keys = [];
          let config = [];
          if (this.chartDatasetType === 1) {
            keys = this.selectedPoisOnlyKeys;
            config = this.poisConfig;
          } else if (this.chartDatasetType === 2) {
            keys = this.selectedAoisOnlyKeys;
            config = this.aoisConfig;
          }
          // add only pois
          keys.forEach(amenity => {
            if (calculationData[amenity]) {
              datasets.push({
                data: calculationData[amenity],
                label: this.$te(`pois.${amenity}`)
                  ? this.$t(`pois.${amenity}`)
                  : amenity,
                fill: false,
                borderColor: config[amenity].color[0] || "rgb(54, 162, 235)",
                borderDash: index === 0 ? [0, 0] : [10, 5],
                pointRadius: 1
              });
            }
          });
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
          scales: {
            yAxes: [
              {
                ticks: {
                  beginAtZero: true
                },
                scaleLabel: {
                  display: true,
                  labelString: this.$t("isochrones.tableData.amenityCount")
                }
              }
            ],
            xAxes: [
              {
                ticks: {
                  beginAtZero: true
                },
                scaleLabel: {
                  display: true,
                  labelString: this.$t("isochrones.tableData.travelTime")
                }
              }
            ]
          },
          animation: {
            duration: 0
          },
          annotation: {
            annotations: [
              {
                id: "current-time-annotation",
                type: "line",
                mode: "vertical",
                scaleID: "x-axis-0",
                borderColor: "red",
                value: this.isochroneRange
              }
            ]
          }
        }
      );
    }
  },
  watch: {
    selectedPoisOnlyKeys: {
      handler: function() {
        this.renderLineChart();
      },
      deep: true
    },
    selectedAoisOnlyKeys: {
      handler: function() {
        this.renderLineChart();
      },
      deep: true
    },
    isochroneRange: function() {
      this.renderLineChart();
    },
    chartDatasetType: function() {
      this.renderLineChart();
    },
    selectedCalculations() {
      this.renderLineChart();
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
