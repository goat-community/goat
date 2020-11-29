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
                beginAtZero: true
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
          if (value >= 0 && value <= 20) {
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
