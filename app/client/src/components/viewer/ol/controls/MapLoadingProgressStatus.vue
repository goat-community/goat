<template>
  <v-progress-circular
    :indeterminate="true"
    :size="70"
    :width="7"
    color="green"
    class="ma-0 pa-0 maploading-status"
    v-show="isNetworkBusy"
  ></v-progress-circular>
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
.v-progress-circular.maploading-status {
  position: absolute;
  width: 100%;
  top: 1em;
  right: 1em;
  z-index: 1;
}
</style>
