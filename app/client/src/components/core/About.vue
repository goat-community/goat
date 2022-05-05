<template>
  <v-dialog v-model="show" scrollable max-width="650px">
    <v-card>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon><v-icon>info</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{ $t("appBar.about.title") }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <v-card-text class="mt-2" primary-title>
          <div>
            <div class="body-1">
              <span>
                <span
                  v-if="$te('appBar.about.whatIs')"
                  v-html="$t('appBar.about.whatIs')"
                ></span>
                <br />
                <span
                  v-if="$te('appBar.about.usedData')"
                  v-html="$t('appBar.about.usedData')"
                ></span>
                <a
                  :style="`color:${appColor.primary}`"
                  class="info-link"
                  href="https://plan4better.de/was-ist-goat/"
                  target="_blank"
                  >{{ $t("appBar.about.moreInfo") }}</a
                >
                <table class="styled-table">
                  <thead>
                    <tr>
                      <th>{{ $t("appBar.about.layerAttributeTable.data") }}</th>
                      <th>
                        {{ $t("appBar.about.layerAttributeTable.source") }}
                      </th>
                      <th>
                        {{
                          $t("appBar.about.layerAttributeTable.yearTimestamp")
                        }}
                      </th>
                    </tr>
                  </thead>
                  <tbody v-if="layerAttributes">
                    <template
                      v-for="(source,
                      propertySource,
                      index1) in layerAttributes"
                    >
                      <template v-for="(date, propertyDate, index2) in source">
                        <tr :key="`${index1.toString()}_${+index2.toString()}`">
                          <td>
                            <template v-for="(layer, index3) in date">
                              <ul
                                :key="
                                  `${index1.toString()}_${+index2.toString()}_${+index3.toString()}`
                                "
                              >
                                <li>
                                  {{
                                    $te(`map.layerName.${layer}`)
                                      ? $t(`map.layerName.${layer}`)
                                      : humanize(layer)
                                  }}
                                </li>
                              </ul>
                            </template>
                          </td>
                          <td>{{ humanize(propertySource) }}</td>
                          <td>{{ propertyDate }}</td>
                        </tr>
                      </template>
                    </template>
                  </tbody>
                </table>
                <br />
                <span
                  v-if="$te('appBar.about.license')"
                  v-html="$t('appBar.about.license')"
                ></span>
              </span>
            </div>
          </div>
        </v-card-text>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>

<script>
import { humanize } from "../../utils/Helpers";
import { mapGetters } from "vuex";
export default {
  props: ["visible"],
  computed: {
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    },
    layerAttributes() {
      let a = {};
      const attributeLayers = [
        ...this.layerConfigList,
        ...(this.appConfig.extra_source || [])
      ];
      attributeLayers.forEach(layer => {
        if (
          (layer.attributes &&
            layer.attributes.source &&
            layer.attributes.date) ||
          (layer.attributes && layer.attributes.source === "openStreetMap")
        ) {
          let { source, date } = layer.attributes;
          if (!a[source]) {
            a[source] = {};
          }
          if (!a[source][date]) {
            a[source][date] = [layer.name];
          } else {
            a[source][date].push(layer.name);
          }
        }
      });
      return a;
    },
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig"
    }),
    ...mapGetters("map", {
      layerConfigList: "layerConfigList"
    })
  },
  methods: {
    humanize
  }
};
</script>

<style scoped>
.v-card__text,
.v-card__title {
  word-break: normal !important;
}
.styled-table {
  border-collapse: collapse;
  margin: 25px 0;
  width: 100%;
  /* margin-left: auto;
  margin-right: auto; */
  font-size: 0.9em;
  font-family: sans-serif;
  min-width: 400px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
}
.styled-table thead tr {
  background-color: #2bb381;
  color: #ffffff;
  text-align: left;
}
.styled-table th,
.styled-table td {
  padding: 12px 15px;
}
.styled-table tbody tr {
  border-bottom: 1px solid #dddddd;
}
.styled-table tbody tr:nth-of-type(even) {
  background-color: #f3f3f3;
}

.styled-table tbody tr:last-of-type {
  border-bottom: 2px solid #2bb381;
}
.styled-table tbody tr.active-row {
  font-weight: bold;
  color: #2bb381;
}
</style>
