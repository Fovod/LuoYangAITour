<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">行程规划测试</h2>

    <!-- 用户输入 -->
    <div class="mb-4 flex flex-col md:flex-row md:items-center gap-2">
      <input
        v-model="userInput"
        type="text"
        placeholder="输入你的需求，例如‘我累了’"
        class="border p-2 flex-1"
      />
      <button @click="sendInput" class="bg-blue-500 text-white p-2 rounded">
        发送
      </button>
      <button @click="generateItinerary" class="bg-green-500 text-white p-2 rounded">
        生成初始行程
      </button>
    </div>

    <!-- AI 回复 -->
    <div class="mb-4">
      <h3 class="font-semibold">AI 回复：</h3>
      <p class="p-2 border">{{ aiReply }}</p>
    </div>

    <!-- 用户偏好 -->
    <div class="mb-4">
      <h3 class="font-semibold">当前偏好：</h3>
      <div v-if="preferences && Object.keys(preferences).length">
        <span v-for="(value, tag) in preferences" :key="tag" class="mr-2">
          {{ tag }}: {{ value }}
        </span>
      </div>
      <p v-else>暂无偏好</p>
    </div>

    <!-- 初始行程表格 -->
    <div class="mb-4">
      <h3 class="font-semibold">初始行程：</h3>
      <table v-if="initialItinerary" class="table-auto border-collapse border border-gray-300 w-full">
        <thead>
          <tr class="bg-gray-200">
            <th class="border px-2 py-1">Day</th>
            <th class="border px-2 py-1">Start</th>
            <th class="border px-2 py-1">Spot</th>
            <th class="border px-2 py-1">Duration(h)</th>
            <th class="border px-2 py-1">Tags</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="day in initialItinerary.plan" :key="day.day">
            <tr v-for="spot in day.spots" :key="spot.name">
              <td class="border px-2 py-1">{{ day.day }}</td>
              <td class="border px-2 py-1">{{ spot.start }}</td>
              <td class="border px-2 py-1">{{ spot.name }}</td>
              <td class="border px-2 py-1">{{ spot.duration }}</td>
              <td class="border px-2 py-1">{{ spot.tags.join(', ') }}</td>
            </tr>
          </template>
        </tbody>
      </table>
      <p v-else>暂无初始行程</p>
    </div>

    <!-- 调整后行程表格 -->
    <div class="mb-4">
      <h3 class="font-semibold">调整后行程：</h3>
      <table v-if="itinerary" class="table-auto border-collapse border border-gray-300 w-full">
        <thead>
          <tr class="bg-gray-200">
            <th class="border px-2 py-1">Day</th>
            <th class="border px-2 py-1">Start</th>
            <th class="border px-2 py-1">Spot</th>
            <th class="border px-2 py-1">Duration(h)</th>
            <th class="border px-2 py-1">Tags</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="day in itinerary.plan" :key="day.day">
            <tr v-for="spot in day.spots" :key="spot.name">
              <td class="border px-2 py-1">{{ day.day }}</td>
              <td class="border px-2 py-1">{{ spot.start }}</td>
              <td class="border px-2 py-1">{{ spot.name }}</td>
              <td class="border px-2 py-1">{{ spot.duration }}</td>
              <td class="border px-2 py-1">{{ spot.tags.join(', ') }}</td>
            </tr>
          </template>
        </tbody>
      </table>
      <p v-else>暂无行程</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'ItineraryTestTable',
  setup() {
    const userInput = ref<string>('')
    const aiReply = ref<string>('')
    const initialItinerary = ref<any>(null)
    const itinerary = ref<any>(null)
    const preferences = ref<Record<string, number>>({})

    // 调用 AI 生成或调整行程
    const sendInput = async () => {
      if (!userInput.value) return

      try {
        const res = await axios.post('http://localhost:8000/test_itinerary', {
          text: userInput.value
        })

        aiReply.value = res.data.reply
        initialItinerary.value = res.data.initial_itinerary
        itinerary.value = res.data.itinerary
        preferences.value = res.data.preferences || {}
        userInput.value = ''
      } catch (e) {
        console.error(e)
        aiReply.value = '请求失败，请检查后端服务是否启动'
      }
    }

    // 仅生成初始行程
    const generateItinerary = async () => {
      try {
        const res = await axios.post('http://localhost:8000/test_itinerary', {
          text: '' // 空输入只生成初始行程
        })
        initialItinerary.value = res.data.initial_itinerary
        itinerary.value = res.data.itinerary
        preferences.value = res.data.preferences || {}
        aiReply.value = '已生成初始行程'
      } catch (e) {
        console.error(e)
        aiReply.value = '生成失败，请检查后端服务是否启动'
      }
    }

    return {
      userInput,
      aiReply,
      initialItinerary,
      itinerary,
      preferences,
      sendInput,
      generateItinerary
    }
  }
})
</script>

<style scoped>
table th, table td {
  border: 1px solid #ccc;
  padding: 4px;
  text-align: left;
}
</style>
