<script>
import { Line } from "vue-chartjs";
import { mapGetters } from "vuex";

export default {
  extends: Line,
  props: {
    chartdata: { type: Object },
    options: { type: Object },
    amenity: { type: Object }
  },
  mounted() {
    this.renderLineChart();
  },
  methods: {
    renderLineChart: function() {
      this.renderChart(
        {
          labels: this.dynamicHeatmapTravelTimes,
          datasets: [
            {
              label: this.$t(
                "appBar.filter.poisSettings.sensitivityGraph.title"
              ),
              fill: false,
              borderColor: "rgb(54, 162, 235)",
              data: this.accessibilityGravityData,
              pointRadius: 2
            }
          ]
        },
        {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            yAxes: [
              {
                ticks: {
                  beginAtZero: true,
                  callback: function(value) {
                    return value + " %";
                  }
                },
                scaleLabel: {
                  display: true,
                  labelString: this.$t(
                    "appBar.filter.poisSettings.sensitivityGraph.gravity"
                  )
                }
              }
            ],
            xAxes: [
              {
                ticks: {
                  beginAtZero: true,
                  callback: function(value) {
                    return (value / 60).toFixed(1);
                  }
                },
                scaleLabel: {
                  display: true,
                  labelString: this.$t(
                    "appBar.filter.poisSettings.sensitivityGraph.travelTime"
                  )
                }
              }
            ]
          }
        }
      );
    }
  },
  watch: {
    amenity: {
      handler: function() {
        this.renderLineChart();
      },
      deep: true
    }
  },
  computed: {
    ...mapGetters("poisaois", {
      dynamicHeatmapTravelTimes: "dynamicHeatmapTravelTimes"
    }),
    accessibilityGravityData() {
      const accessibilityGravity = this.dynamicHeatmapTravelTimes.map(
        x => Math.exp(-(x * x) / this.amenity.sensitivity) * 100
      );
      return accessibilityGravity;
    }
  }
};
</script>
