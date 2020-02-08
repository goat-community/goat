<template>
  <v-progress-linear
    :indeterminate="true"
    color="green"
    height="5"
    class="ma-0 pa-0 maploading-status"
    v-show="isNetworkBusy"
  ></v-progress-linear>
</template>

<script>
export default {
  name: "progress-status",
  props: {
    isNetworkBusy: { type: Boolean, required: true }
  }
};
</script>
<style>
.v-progress-linear.maploading-status {
  position: fixed;
  width: 100%;
  top: 0em;
  left: 0em;
  z-index: 1;
}
</style>
