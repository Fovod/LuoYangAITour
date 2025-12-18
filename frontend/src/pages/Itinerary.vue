<template>
  <div class="max-w-4xl mx-auto p-6">
    <!-- 标题区 -->
    <header class="mb-6 border-b pb-4">
      <h1 class="text-2xl font-bold text-gray-800">行程规划测试</h1>
      <p class="text-gray-500 text-sm">End-to-End 测试模式：直接输入指令修改 JSON</p>
    </header>

    <!-- 1. 控制区：输入指令 -->
    <div class="bg-gray-50 p-4 rounded-lg shadow-sm border mb-6">
      <div class="flex gap-2">
        <input
          v-model="userInput"
          @keyup.enter="sendInput"
          type="text"
          placeholder="输入指令（例：'饿了想吃面'、'太累了要休息'、'把龙门石窟换成白马寺'）..."
          class="flex-1 border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black" 
          :disabled="loading"
        />
        <button 
          @click="sendInput" 
          :disabled="loading"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium disabled:bg-gray-400 transition"
        >
          {{ loading ? '思考中...' : '发送指令' }}
        </button>
        <button 
          @click="resetPlan" 
          class="bg-red-100 hover:bg-red-200 text-red-600 px-4 py-2 rounded border border-red-200"
        >
          重置/初始化
        </button>
      </div>
    </div>

    <!-- 2. 反馈区：AI 回复 & 状态 -->
    <div v-if="aiReply" class="mb-6 flex gap-4">
      <!-- 左侧：AI 角色回复 -->
      <div class="flex-1 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
        <div class="font-bold text-blue-800 mb-1">导游李白：</div>
        <p class="text-gray-700">{{ aiReply }}</p>
      </div>
      
      <!-- 右侧：检测到的偏好 (调试用) -->
      <div class="w-1/3 bg-gray-100 p-4 rounded border text-sm">
        <div class="font-bold text-gray-600 mb-2">用户偏好/状态权重</div>
        <div v-if="Object.keys(preferences).length > 0" class="flex flex-wrap gap-2">
          <span 
            v-for="(val, key) in preferences" 
            :key="key"
            class="bg-white border px-2 py-1 rounded text-xs text-gray-600"
          >
            {{ key }}: {{ val.toFixed(1) }}
          </span>
        </div>
        <div v-else class="text-gray-400 italic">暂无偏好数据</div>
      </div>
    </div>

    <!-- 3. 展示区：最新行程表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden border">
      <div class="bg-gray-100 px-4 py-2 border-b font-bold text-gray-700 flex justify-between items-center">
        <span>📅 当前行程表</span>
        <span class="text-xs font-normal text-gray-500" v-if="itinerary">共 {{ itinerary.plan.length }} 天</span>
      </div>

      <div v-if="!itinerary" class="p-8 text-center text-gray-400">
        暂无行程，请在上方输入“帮我规划行程”或点击“重置/初始化”
      </div>

      <div v-else>
        <div v-for="day in itinerary.plan" :key="day.day" class="border-b last:border-b-0">
          <!-- 天数标题 -->
          <div class="bg-gray-50 px-4 py-2 font-semibold text-sm text-gray-600">
            第 {{ day.day }} 天
          </div>
          
          <!-- 景点列表 -->
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="text-gray-500 border-b">
                <th class="px-4 py-2 font-medium w-24">时间</th>
                <th class="px-4 py-2 font-medium">地点 / 活动</th>
                <th class="px-4 py-2 font-medium w-20">时长</th>
                <th class="px-4 py-2 font-medium">标签</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="spot in day.spots" 
                :key="spot.name + spot.start"
                class="border-b last:border-b-0 hover:bg-gray-50 transition"
                :class="getRowClass(spot)"
              >
                <td class="px-4 py-3 font-mono text-gray-600">{{ spot.start }}</td>
                <td class="px-4 py-3 font-medium text-gray-800 flex items-center gap-2">
                  <span>{{ spot.name }}</span>
                  <!-- 简单的图标标记 -->
                  <span v-if="isDining(spot)" title="用餐">🍜</span>
                  <span v-if="isRest(spot)" title="休息">☕</span>
                </td>
                <td class="px-4 py-3 text-gray-600">{{ spot.duration }}h</td>
                <td class="px-4 py-3">
                  <span 
                    v-for="tag in spot.tags" 
                    :key="tag"
                    class="inline-block bg-gray-200 rounded-full px-2 py-0.5 text-xs text-gray-600 mr-1"
                  >
                    {{ tag }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'ItineraryConsole',
  setup() {
    const userInput = ref('')
    const aiReply = ref('')
    const itinerary = ref<any>(null)
    const preferences = ref<any>({})
    const loading = ref(false)

    // 发送指令
    const sendInput = async () => {
      if (!userInput.value.trim()) return
      
      loading.value = true
      try {
        // 注意：这里只需要接收 itinerary 一个字段即可
        const res = await axios.post('http://localhost:8000/test_itinerary', {
          text: userInput.value
        })
        
        aiReply.value = res.data.reply
        itinerary.value = res.data.itinerary
        preferences.value = res.data.preferences || {}
        
        // 发送成功后清空输入框
        userInput.value = ''
      } catch (e) {
        console.error(e)
        aiReply.value = '❌ 请求出错，请检查后端是否启动'
      } finally {
        loading.value = false
      }
    }

    // 重置按钮（发送特定的初始化指令）
    const resetPlan = () => {
      userInput.value = '重新规划一个洛阳一日游'
      sendInput()
    }

    // --- 辅助函数：用来给表格行加颜色 ---
    
    // 判断是否是吃饭
    const isDining = (spot: any) => {
      const name = spot.name || ''
      return name.includes('饭') || name.includes('面') || name.includes('汤') || name.includes('餐厅') || name.includes('吃')
    }

    // 判断是否是休息
    const isRest = (spot: any) => {
      const name = spot.name || ''
      const tags = spot.tags || []
      return name.includes('休息') || name.includes('下午茶') || tags.includes('rest')
    }

    // 根据类型返回这一行的背景色类名
    const getRowClass = (spot: any) => {
      if (isDining(spot)) return 'bg-orange-50' // 吃饭显示淡橙色
      if (isRest(spot)) return 'bg-green-50'    // 休息显示淡绿色
      return ''
    }

    return {
      userInput,
      aiReply,
      itinerary,
      preferences,
      loading,
      sendInput,
      resetPlan,
      getRowClass,
      isDining,
      isRest
    }
  }
})
</script>

<style scoped>
/* 简单的输入框美化 */
input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}
</style>