import { createRouter, createWebHistory } from "vue-router";
import Chat from "../pages/Chat.vue";
import Itinerary from "../pages/Itinerary.vue";
import Home from "../pages/Home.vue";

const routes = [
    {
        path:'/',
        redirect:'/home',
    },
    {
        path:'/home',
        redirect:Home,
    },
    {
        path:'/chat',
        component:Chat,
    },
    {
        path:'/test_itinerary',
        component:Itinerary,
    }
]

const router = createRouter({
    history:createWebHistory(),
    routes,
})

export default router