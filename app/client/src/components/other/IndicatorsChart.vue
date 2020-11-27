<script>
import { HorizontalBar } from "vue-chartjs";
import {
  LinearColorInterpolator,
  ColorObj,
  humanize
} from "../../utils/Helpers";
// import { mapGetters } from "vuex";

export default {
  extends: HorizontalBar,
  props: {
    chartdata: { type: Object },
    options: { type: Object },
    feature: { type: Object }
  },
  data() {
    return {
      exludedProps: ["id", "geom", "geometry", "layerName"],
      colors: {
        very_bad: {
          lower: "#b64a4c",
          upper: "#ff8688"
        },
        bad: {
          lower: "#ff8688",
          upper: "#ffe70e"
        },
        medium: {
          lower: "#ff8688",
          upper: "#ffe70e"
        },
        good: {
          lower: "#ffe70e",
          upper: "#45b64f"
        },
        very_good: {
          lower: "#45b64f",
          upper: "#3f8437"
        },
        default: {
          lower: "#000000",
          upper: "#000000"
        }
      }
    };
  },
  mounted() {
    this.renderBarChart();
  },
  methods: {
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
        {
          options: {
            tooltips: {
              enabled: false
            },
            legend: {
              position: "bottom",
              display: true,
              labels: { usePointStyle: true }
            },
            scales: {
              yAxes: [
                {
                  gridLines: {
                    offsetGridLines: true
                  },
                  ticks: {
                    beginAtZero: true,
                    min: 0
                  },
                  barPercentage: 1,
                  categoryPercentage: 1
                }
              ],
              xAxes: [
                {
                  gridLines: {
                    offsetGridLines: true
                  },
                  ticks: {
                    beginAtZero: true,
                    min: 0
                  }
                }
              ]
            }
          }
        }
      );
    }
  },
  watch: {
    feature: {
      handler: function() {
        this.renderBarChart();
      },
      deep: true
    }
  },
  computed: {
    indicators() {
      const properties = Object.keys(this.feature.getProperties());
      const labels = [];
      const data = [];
      const colorData = [];
      properties.forEach(prop => {
        if (!this.exludedProps.includes(prop)) {
          const value = this.feature.get(prop);
          labels.push(this.$t(`charts.indicators.${prop}` || humanize(prop)));
          data.push(this.feature.get(prop));
          // Find the correct color based on value
          let color;
          let colorPercentage;
          if (value <= 20 && value >= 0) {
            color = this.colors["very_bad"];
            colorPercentage = ((value - 0) / (20 - 0)) * 100;
          } else if (value <= 40 && value >= 21) {
            color = this.colors["bad"];
            colorPercentage = ((value - 21) / (40 - 21)) * 100;
          } else if (value <= 60 && value >= 41) {
            color = this.colors["medium"];
            colorPercentage = ((value - 41) / (60 - 41)) * 100;
          } else if (value <= 80 && value >= 61) {
            color = this.colors["good"];
            colorPercentage = ((value - 61) / (80 - 61)) * 100;
          } else if (value <= 100 && value >= 81) {
            color = this.colors["very_good"];
            colorPercentage = ((value - 81) / (100 - 81)) * 100;
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
