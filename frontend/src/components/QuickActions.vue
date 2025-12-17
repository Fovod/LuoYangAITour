<template>
  <div class="quick-actions">
    <button @click="$emit('action', '推荐餐厅')">推荐餐厅</button>
    <button @click="$emit('action', '推荐景点')">推荐景点</button>
    <button @click="$emit('action', '休息')">休息</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({});
</script>

<style scoped>
.quick-actions button {
  margin-right: 5px;
}
</style>
