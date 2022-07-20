<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="700">
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="success" dark v-bind="attrs" v-on="on">
          Import External Layer
        </v-btn>
      </template>

      <v-card style="padding: 40px;">
        <div v-if="option === 'first'">
          <v-card-text class="pa-0">
            <h1 class="mb-4">Import a Layer</h1>
          </v-card-text>
          <div>
            <v-btn
              class="success button-categorizer"
              @click="changeOption('builtin')"
              >Add Built-in Layers</v-btn
            >
            <v-btn
              class="success button-categorizer"
              @click="changeOption('upload')"
              >Upload Layer via source url</v-btn
            >
          </div>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="success"
              style="margin-top: 20px"
              text
              @click="cancelHandler"
              >Cancel</v-btn
            >
          </v-card-actions>
        </div>
        <div v-if="option === 'upload'">
          <v-card-text class="pa-0">
            <h1 class="mb-4">Import a Layer</h1>
            <v-form ref="form" lazy-validation>
              <v-text-field
                v-model="url"
                label="Source Url"
                required
              ></v-text-field>
            </v-form>
            <div>
              <p class="h6">Results</p>
              <v-card
                v-for="(simpleLayer, idx) in layerListToAdd"
                :key="idx"
                class="mx-auto mb-2"
                style="display: flex"
              >
                <v-card-text>
                  <div>{{ simpleLayer.title }}</div>
                  <p>{{ simpleLayer.url }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    text
                    @click="$emit('getLayerInfo', simpleLayer)"
                    color="deep-purple accent-4"
                  >
                    <v-icon small color="success">fas fa-circle-plus</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="success" text @click="cancelHandler">Cancel</v-btn>
            <v-btn color="success" text @click="layerDataHandler">
              Import Layers
            </v-btn>
          </v-card-actions>
        </div>
        <div v-if="option === 'builtin'">
          <v-card-text class="pa-0">
            <h1 class="mb-4">Built-in Layers</h1>
          </v-card-text>
          <v-bottom-navigation :value="value" color="primary" horizontal>
            <v-btn @click="value = 0">
              <span>Backgroung Layers</span>
            </v-btn>

            <v-btn @click="value = 1">
              <span>Additional Data</span>
            </v-btn>

            <v-btn @click="value = 2">
              <span>Buildings and Land Use</span>
            </v-btn>

            <v-btn @click="value = 3">
              <span>Environmental Data</span>
            </v-btn>
          </v-bottom-navigation>

          <div class="cards">
            <div
              v-for="(layer, idx) in dummyLayerData[value].layers"
              :key="idx"
              class="cardBox"
              @click="$emit('addLayer', layer)"
            >
              <div class="overlay">+</div>
              <img :src="layer.img" alt="" />
              <div class="content">
                <p>{{ layer.name }}</p>
              </div>
            </div>
          </div>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="success" text @click="cancelHandler">Cancel</v-btn>
          </v-card-actions>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { dataBuiltInLayers } from "../../../testData";

export default {
  data: () => ({
    url: "",
    dialog: false,
    error: "",
    layerListToAdd: [],
    option: "first",
    value: 0,
    dummyLayerData: []
  }),
  mounted() {
    this.dummyLayerData = dataBuiltInLayers;
  },
  methods: {
    changeOption(value) {
      this.option = value;
    },
    cancelHandler() {
      this.url = "";
      this.layerListToAdd = [];
      this.error = "";
      this.dialog = false;
      this.option = "first";
    },
    layerDataHandler() {
      if (this.url !== "") {
        this.error = "";
        this.layerListToAdd = [];
        const data = {
          layer_url: this.url
        };
        this.findAllAvailableLayers(data);
        // this.dialog = false;
        this.url = "";
      } else {
        this.error = "Make sure to fill all the required fields";
      }
    },
    findAllAvailableLayers(data) {
      fetch(data.layer_url)
        .then(result => result.text())
        .then(datares => {
          let parser = new DOMParser(),
            xmlDoc = parser.parseFromString(datares, "text/xml");
          let names = [...xmlDoc.getElementsByTagName("Layer")];
          let type = xmlDoc.getElementsByTagName("Name")[0].textContent;
          names.forEach((layerElement, idx) => {
            if (idx !== 0) {
              let layerPossibility = {
                title: layerElement.getElementsByTagName("Title")[0]
                  .textContent,
                name: layerElement.getElementsByTagName("Name")[0].textContent,
                url: data.layer_url.split("?")[0] + "?",
                type: type
              };
              this.layerListToAdd.push(layerPossibility);
            }
          });
        })
        .catch(err => (this.error = err));
    }
  }
};
</script>

<style scoped>
.button-categorizer {
  width: 100%;
  margin-top: 20px;
}

.cards {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  grid-row-gap: 20px;
  justify-items: center;
  margin-top: 20px;
}

.cardBox {
  width: 90px;
  height: 120px;
  cursor: pointer;
  position: relative;
  box-shadow: rgba(100, 100, 111, 0.2) 0px 7px 29px 0px;
}

.cardBox img {
  width: 100%;
  height: 70%;
  object-fit: cover;
}

.cardBox .content {
  width: 100%;
  height: 30%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.cardBox .content p {
  font-size: 10px;
  font-weight: 600;
}

.overlay {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 70%;
  background: rgba(0, 0, 0, 0.474);
  display: flex;
  justify-content: center;
  align-items: center;
  color: rgb(188, 188, 188);
  font-weight: bolder;
  font-size: 45px;
  transition: all 0.15s ease-in-out;
}

.overlay:hover {
  color: white;
  background: rgba(0, 0, 0, 0.274);
}
</style>
