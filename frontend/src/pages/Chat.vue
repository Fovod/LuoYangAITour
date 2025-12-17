<template>
  <div class="chat-container">
    <HeaderStatus :role="role" :location="location" :time="time"/>
    <div class="chat-bubbles">
      <ChatBubble v-for="(msg,i) in messages" :key="i" :message="msg"/>
    </div>
    <QuickActions @action="onAction"/>
    <div class="input-box">
      <input v-model="inputText" @keyup.enter="() => sendMessage()"/>
      <button @click="() => sendMessage()">发送</button>
    </div>
  </div>
</template>

<script lang="ts">
    import { defineComponent, ref } from 'vue';
    import ChatBubble from '../components/ChatBubble.vue';
    import QuickActions from '../components/QuickActions.vue';
    import HeaderStatus from '../components/HeaderStatus.vue';
    import { sendMessage as apiSendMessage } from '../services/api';

    export default defineComponent({
    components: { ChatBubble, QuickActions, HeaderStatus },
    setup() {
        const inputText = ref('');
        const messages = ref<{sender:string, text:string}[]>([]);
        const role = ref('李白');
        const location = ref('洛阳古城');
        const time = ref('上午9点');

        async function sendMessage(content?: string) {
        const text = content ?? inputText.value;
        if (!text || text.trim() === '') return; // 避免空字符串发送
        messages.value.push({ sender: 'user', text });
        try {
            const reply = await apiSendMessage('user_123', text);
            messages.value.push({ sender: 'ai', text: reply ?? 'AI 没有回复' });
        } catch(err) {
            console.error(err);
            messages.value.push({ sender: 'ai', text: '请求出错' });
        }
        inputText.value = '';
        }

        function onAction(action: string) {
        sendMessage(action);
        }

        return { inputText, messages, role, location, time, sendMessage, onAction };
    }
    });
</script>

<style>
.chat-container { display:flex; flex-direction:column; height:100vh; }
.chat-bubbles { flex:1; overflow-y:auto; padding:10px; }
.input-box { display:flex; padding:5px; }
input { flex:1; padding:5px; }
</style>
