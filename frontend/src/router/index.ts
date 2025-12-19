import { createRouter, createWebHistory } from "vue-router";
import Home from "../pages/Home.vue";

const routes = [
    {
        path:'/',
        redirect:'/home',
    },
    {
        path:'/home',
        component:Home,
    },
]

const router = createRouter({
    history:createWebHistory(),
    routes,
})

export default router