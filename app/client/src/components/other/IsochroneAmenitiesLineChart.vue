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
      let labels = [...accessibilityData[accessibilityKeys[0]].keys()];
      labels = labels.map(num => num + 1);
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
            borderColor: this.preDefCalculationColors[calculation.id - 1],
            borderDash: index === 0 ? [0, 0] : [10, 5],
            pointRadius: 1,
            tension: 0
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
                tension: 0,
                borderColor: config[amenity].color[0] || "rgb(54, 162, 235)",
                borderDash: index === 0 ? [0, 0] : [10, 5],
                pointRadius: 1
              });
            }
          });
        }
      });

      let labelString = "";
      if (this.chartDatasetType === 0) {
        labelString = this.$t("isochrones.tableData.populationCount");
      } else if (this.chartDatasetType === 1) {
        labelString = this.$t("isochrones.tableData.amenityCount");
      } else if (this.chartDatasetType === 2) {
        labelString = this.$t("isochrones.tableData.aoisArea");
      }

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
                  beginAtZero: true,
                  min: 0
                },
                scaleLabel: {
                  display: true,
                  labelString: labelString
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
              ...this.selectedCalculations.map(calc => {
                return {
                  id: `current-time-annotation-${calc.id}`,
                  type: "line",
                  mode: "vertical",
                  scaleID: "x-axis-0",
                  borderColor: this.calculationColors[calc.id - 1],
                  value: this.calculationTravelTime[calc.id - 1]
                };
              })
            ]
          },
          legend: {
            labels: {
              filter: function(legendItem) {
                if (
                  legendItem &&
                  legendItem.lineDash[0] !== 0 &&
                  legendItem.lineDash[1] !== 0
                ) {
                  return false;
                }
                return true;
              }
            }
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
    calculationTravelTime: function() {
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
      preDefCalculationColors: "preDefCalculationColors",
      calculationTravelTime: "calculationTravelTime",
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
