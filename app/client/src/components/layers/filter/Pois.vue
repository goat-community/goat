<template>
  <v-treeview
    v-model="tree"
    :open="open"
    :items="allPois"
    ref="poisTree"
    activatable
    open-on-click
    selectable
    return-object
    item-key="name"
    selected-color="green"
    active-class="grey lighten-4 indigo--text"
    on-icon="check_box"
    off-icon="check_box_outline_blank"
    indeterminate-icon="indeterminate_check_box"
  >
    <template v-slot:prepend="{ item, open }">
      <img v-if="item.icon" class="pois-icon" :src="getPoisIconUrl(item)" />
    </template>
    <template v-slot:append="{ item, open }">
      <template v-if="item.icon">
        <v-icon @click="increaseWeight(item)" small class="arrow-icons mr-1">
          fas fa-arrow-up
        </v-icon>
        <span>{{ item.weight }}</span>
        <v-icon @click="decreaseWeight(item)" small class="arrow-icons ml-1">
          fas fa-arrow-down
        </v-icon>
      </template>
    </template>
  </v-treeview>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
export default {
  data: () => ({
    open: [],
    tree: []
  }),
  methods: {
    ...mapActions("pois", {
      updateSelectedPois: "updateSelectedPois"
    }),
    getPoisIconUrl(item) {
      var images = require.context(
        "../../../assets/img/pois/",
        false,
        /\.png$/
      );
      return images("./" + item.icon + ".png");
    },
    increaseWeight(item) {
      if (item.weight < 10) {
        item.weight++;
      }
    },
    decreaseWeight(item) {
      if (item.weight > 1) {
        item.weight--;
      }
    }
  },
  watch: {
    tree: function() {
      let me = this;
      me.updateSelectedPois(me.tree);
    }
  },
  computed: {
    ...mapGetters("pois", {
      allPois: "allPois"
    })
  }
};
</script>
<style>
.arrow-icons {
  color: "#4A4A4A";
}
.arrow-icons:hover {
  cursor: pointer;
  color: #30c2ff;
}

.pois-icon {
  margin-bottom: 13px;
}
.v-treeview-node--leaf {
  margin-left: 30px;
}
.v-treeview-node__content,
.v-treeview-node__label {
  flex-shrink: 1;
}

.v-treeview-node__root {
  min-height: 34px;
  height: auto;
}
</style>
