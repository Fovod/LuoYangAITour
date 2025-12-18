<template>
  <div class="flex h-screen bg-gray-100 overflow-hidden">
    
    <!-- 左侧：聊天区域 (占 40%) -->
    <div class="w-2/5 flex flex-col bg-white border-r shadow-lg z-10">
      <!-- 头部 -->
      <div class="p-4 border-b bg-blue-600 text-white shadow-md">
        <h2 class="text-lg font-bold flex items-center gap-2">
          🤖 洛阳导游 - 李白
        </h2>
        <p class="text-xs opacity-80 mt-1">当前状态: {{ intentLog || '待命' }}</p>
      </div>

      <!-- 消息列表 -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50" ref="msgContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="flex" 
          :class="msg.sender === 'user' ? 'justify-end' : 'justify-start'"
        >
          <!-- 消息气泡 -->
          <div 
            class="max-w-[80%] rounded-2xl px-4 py-3 shadow-sm text-sm leading-relaxed"
            :class="msg.sender === 'user' ? 'bg-blue-500 text-white rounded-br-none' : 'bg-white text-gray-800 border rounded-bl-none'"
          >
            <!-- 发送者名字 -->
            <div class="text-xs font-bold mb-1 opacity-70">
              {{ msg.sender === 'user' ? '我' : '李白' }}
            </div>
            <!-- 内容 -->
            <div class="whitespace-pre-wrap">{{ msg.text }}</div>
          </div>
        </div>
        
        <!-- Loading 动画 -->
        <div v-if="loading" class="flex justify-start">
          <div class="bg-gray-200 text-gray-500 text-xs rounded-full px-4 py-2 animate-pulse">
            李白正在思考...
          </div>
        </div>
      </div>

      <!-- 底部输入框 + 快捷 Action -->
      <div class="p-4 bg-white border-t">
        <!-- 快捷 Action 按钮 (优化版) -->
        <div class="flex gap-2 mb-3 overflow-x-auto pb-1 no-scrollbar">
          <button @click="sendText('帮我规划行程')" class="action-chip">📅 规划行程</button>
          <button @click="sendText('我饿了，推荐好吃的')" class="action-chip">🍜 找美食</button>
          <button @click="sendText('太累了，想休息')" class="action-chip">😴 休息一会</button>
          <button @click="sendText('我想去龙门石窟')" class="action-chip">🏔️ 去龙门</button>
        </div>

        <div class="flex gap-2">
          <input 
            v-model="inputText" 
            @keyup.enter="handleSend"
            type="text" 
            placeholder="和李白聊聊你的旅行计划..." 
            class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            :disabled="loading"
          />
          <button 
            @click="handleSend" 
            :disabled="!inputText || loading"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-lg font-medium disabled:bg-gray-300 transition"
          >
            发送
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧：行程可视化 (占 60%) -->
    <div class="w-3/5 h-full overflow-y-auto bg-gray-100 p-6">
      <div class="bg-white rounded-xl shadow-sm border min-h-[500px]">
        <div class="p-4 border-b flex justify-between items-center bg-gray-50 rounded-t-xl">
          <h3 class="font-bold text-gray-700">📅 行程预览</h3>
          <span class="text-xs text-gray-400" v-if="itinerary">自动同步中</span>
        </div>

        <div v-if="!itinerary" class="flex flex-col items-center justify-center h-64 text-gray-400">
          <div class="text-4xl mb-2">🗺️</div>
          <p>暂无行程，请在左侧告诉李白你的需求</p>
        </div>

        <div v-else class="p-6">
          <div v-for="day in itinerary.plan" :key="day.day" class="mb-8 last:mb-0 relative pl-6 border-l-2 border-blue-200">
            <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-500 border-2 border-white"></div>
            <h4 class="font-bold text-lg text-gray-800 mb-4">第 {{ day.day }} 天</h4>
            
            <div class="space-y-3">
              <!-- 行程卡片 -->
              <div 
                v-for="spot in day.spots" 
                :key="spot.start"
                class="bg-white border rounded-lg p-3 hover:shadow-md transition-shadow flex gap-4 items-center group"
                :class="getCardStyle(spot)"
              >
                <!-- 时间 -->
                <div class="w-16 text-center border-r pr-4">
                  <div class="font-mono font-bold text-gray-700">{{ spot.start }}</div>
                  <div class="text-xs text-gray-400">{{ spot.duration }}小时</div>
                </div>

                <!-- 内容 -->
                <div class="flex-1">
                  <div class="font-bold text-gray-800">{{ spot.name }}</div>
                  <div class="flex gap-2 mt-1">
                    <span 
                      v-for="tag in spot.tags" 
                      :key="tag"
                      class="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                    >
                      #{{ tag }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, nextTick } from 'vue';
import axios from 'axios';

export default defineComponent({
  setup() {
    const inputText = ref('');
    const messages = ref<{sender: string, text: string}[]>([
      { sender: 'ai', text: '客官好！我是李白。想去哪里游玩？或者是想听听我的诗？' }
    ]);
    const itinerary = ref<any>(null);
    const loading = ref(false);
    const intentLog = ref(''); // 用来显示当前 Planner 决策 (调试用)
    const msgContainer = ref<HTMLElement | null>(null);

    // 滚动到底部
    const scrollToBottom = async () => {
      await nextTick();
      if (msgContainer.value) {
        msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
      }
    };

    const sendText = (text: string) => {
      inputText.value = text;
      handleSend();
    };

    const handleSend = async () => {
      const text = inputText.value.trim();
      if (!text || loading.value) return;

      // 1. 添加用户消息
      messages.value.push({ sender: 'user', text });
      inputText.value = '';
      loading.value = true;
      scrollToBottom();

      try {
        // 2. 请求后端
        const res = await axios.post('http://localhost:8000/test_itinerary', { text });
        
        // 3. 更新回复
        messages.value.push({ sender: 'ai', text: res.data.reply });
        
        // 4. 更新行程 (如果有变化)
        if (res.data.itinerary) {
          itinerary.value = res.data.itinerary;
        }

        // 5. 显示 Intent (查看是 chat 还是 update_plan)
        if (res.data.debug_intent) {
          const i = res.data.debug_intent.intent;
          intentLog.value = i === 'update_plan' ? '正在规划行程...' : '正在闲聊...';
        }

      } catch (e) {
        messages.value.push({ sender: 'ai', text: '抱歉，我好像喝醉了（服务器错误）' });
      } finally {
        loading.value = false;
        scrollToBottom();
      }
    };

    // 样式辅助
    const getCardStyle = (spot: any) => {
      const name = spot.name || '';
      if (name.includes('饭') || name.includes('吃')) return 'border-orange-200 bg-orange-50';
      if (name.includes('休息') || name.includes('茶')) return 'border-green-200 bg-green-50';
      return 'border-gray-200';
    };

    return { 
      inputText, messages, itinerary, loading, intentLog, msgContainer, 
      handleSend, sendText, getCardStyle 
    };
  }
});
</script>

<style scoped>
.action-chip {
  @apply px-3 py-1 bg-gray-100 hover:bg-blue-100 text-blue-600 text-xs rounded-full border border-gray-200 transition whitespace-nowrap;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>