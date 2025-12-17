<template>
  <div class="chat-bubble">
    <strong>{{ message.sender }}:</strong> {{ message.text }}
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';


export default defineComponent({
  props: {
    message: {
      type: Object as PropType<{ sender: string; text: string }>,
      required: true,
    },
  },
});
</script>

<style scoped>
.chat-bubble {
  margin-bottom: 5px;
}
</style>
