import { createRouter, createWebHistory } from "vue-router";
import Chat from "../pages/Chat.vue";
import Itinerary from "../pages/Itinerary.vue";

const routes = [
    {
        path:'/',
        redirect:'/chat',
    },
    {
        path:'/chat',
        component:Chat,
    },
    {
        path:'/test_itinerary',
        component:Itinerary
    }
]

const router = createRouter({
    history:createWebHistory(),
    routes,
})

export default router