<template>
  <div class="header-status">
    角色: {{ role }} | 地点: {{ location }} | 时间: {{ time }}
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';


export default defineComponent({
  props: {
    role: { type: String, required: true },
    location: { type: String, required: true },
    time: { type: String, required: true },
  },
});
</script>

<style scoped>
.header-status {
  padding: 5px;
  font-weight: bold;
}
</style>
