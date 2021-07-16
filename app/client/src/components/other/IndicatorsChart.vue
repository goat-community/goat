<script>
import { HorizontalBar } from "vue-chartjs";
import { EventBus } from "../../EventBus";

import {
  LinearColorInterpolator,
  ColorObj,
  humanize
} from "../../utils/Helpers";
// import { mapGetters } from "vuex";

export default {
  extends: HorizontalBar,
  props: {
    feature: { type: Object }
  },
  data() {
    return {
      exludedProps: ["id", "geom", "geometry", "layerName"],
      attributes: {
        sidewalk_quality: ["sidewalk", "incline_percent", "surface", "highway"],
        traffic_protection: [
          "lanes",
          "maxspeed",
          "crossings",
          "parking",
          "cnt_accidents",
          "noise_day",
          "noise_night"
        ],
        security: ["lit_classified", "covered"],
        green_blue_index: ["vegetation", "water"],
        liveliness: ["landuse", "pois", "population"],
        comfort: [
          "cnt_benches",
          "cnt_waste_baskets",
          "cnt_toilets",
          "cnt_fountains"
        ],
        data_quality: [],
        walkability: []
      },
      colors: {
        very_bad: {
          lower: "#c10707",
          upper: "#be987f"
        },
        bad: {
          lower: "#ed8137",
          upper: "#ed8137"
        },
        medium: {
          lower: "#fec107",
          upper: "#9fbe36"
        },
        good: {
          lower: "#a0bf3c",
          upper: "#61953d"
        },
        very_good: {
          lower: "#659843",
          upper: "#385723"
        },
        default: {
          lower: "#000000",
          upper: "#000000"
        },
        data_quality: {
          lower: "#808080",
          upper: "#808080"
        }
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          display: false
        },
        scales: {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
                callback: value => {
                  return (
                    this.$t(`charts.indicators.${value}`) || humanize(value)
                  );
                }
              }
            }
          ],
          xAxes: [
            {
              ticks: {
                beginAtZero: true
              },
              scaleLabel: {
                display: true
              }
            }
          ]
        },
        tooltips: {
          displayColors: false,
          titleFontSize: 15,
          bodyFontSize: 12,
          titleFontStyle: "bold",
          bodyFontStyle: "bold",
          callbacks: {
            title: function(tooltipItem) {
              const attr = tooltipItem[0].label;
              const label = this.$te(`charts.indicators.${attr}`)
                ? this.$t(`charts.indicators.${attr}`)
                : humanize(attr);
              const value = tooltipItem[0].value;
              return `${label}: ${value ? value : "--"}`;
            }.bind(this),
            label: function(tooltipItem) {
              const labels = [];
              const attrLabel = tooltipItem.label;
              // const attrValue = tooltipItem.value;
              const props = this.attributes[attrLabel];
              if (Array.isArray(props)) {
                props.forEach(prop => {
                  const label = this.$te(`charts.indicators.${prop}`)
                    ? this.$t(`charts.indicators.${prop}`)
                    : humanize(prop);
                  const value = this.feature.get(prop);
                  if (label) {
                    labels.push(`${label}: ${value ? value : "--"}`);
                  }
                });
              }
              return labels;
            }.bind(this)
          }
        }
      }
    };
  },
  mounted() {
    this.init();
    EventBus.$on("ol-interaction-activated", interaction => {
      if (interaction === "languageChange") {
        this.init();
      }
    });
  },
  methods: {
    init() {
      this.renderBarChart();
    },
    renderBarChart: function() {
      this.renderChart(
        {
          labels: this.indicators.labels,
          datasets: [
            {
              backgroundColor: this.indicators.colorData,
              data: this.indicators.data
            }
          ]
        },
        this.options
      );
    }
  },
  watch: {
    feature: {
      handler: function() {
        this.init();
      },
      deep: true
    }
  },
  computed: {
    indicators() {
      const properties = Object.keys(this.attributes);
      const labels = [];
      const data = [];
      const colorData = [];
      properties.forEach(prop => {
        if (!this.exludedProps.includes(prop)) {
          let value = this.feature.get(prop);

          labels.push(prop);
          // Data quality (edge case) multiple with 100 (REMOVE if value is between 0 and 100)
          if (prop === "data_quality" && Number.isFinite(value)) {
            value = value * 100;
          }
          if (Number.isFinite(value)) {
            value = value.toFixed(0);
          }
          data.push(value);

          // Find the correct color based on value
          let color;
          let colorPercentage;
          if (prop === "data_quality") {
            color = this.colors["data_quality"];
            colorPercentage = 100;
          } else if (value >= 0 && value <= 20) {
            color = this.colors["very_bad"];
            colorPercentage = ((value - 0) / 20) * 100;
          } else if (value > 20 && value <= 40) {
            color = this.colors["bad"];
            colorPercentage = ((value - 20) / 20) * 100;
          } else if (value > 40 && value <= 60) {
            color = this.colors["medium"];
            colorPercentage = ((value - 40) / 20) * 100;
          } else if (value > 60 && value <= 80) {
            color = this.colors["good"];
            colorPercentage = ((value - 60) / 20) * 100;
          } else if (value > 80 && value <= 100) {
            color = this.colors["very_good"];
            colorPercentage = ((value - 80) / 20) * 100;
          } else {
            // Fallback if there is not in range
            color = this.colors["default"];
            colorPercentage = 100;
          }
          const lower = new ColorObj(color.lower);
          const upper = new ColorObj(color.upper);
          const backgroundColor = LinearColorInterpolator.findColorBetween(
            lower,
            upper,
            colorPercentage
          ).asRgbCss();
          colorData.push(backgroundColor);
        }
      });
      return {
        labels,
        data,
        colorData
      };
    }
  }
};
</script>
