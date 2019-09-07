<template>
  <v-expansion-panels
    dark
    style="position:absolute;bottom:30px;right:10px;maxWidth: 200px;"
  >
    <v-expansion-panel style="background-color: white;">
      <v-expansion-panel-header
        >Layers Legend
        <template v-slot:actions>
          <v-icon small>$vuetify.icons.expand</v-icon>
        </template>
      </v-expansion-panel-header>
      <v-expansion-panel-content> </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<script>
export default {};
</script>
<style lang="scss" scoped>
.v-expansion-panel-header {
  min-height: 30px;
  padding: 5px;
  background-color: #4caf50;
}
</style>
