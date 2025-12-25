<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const isAuthPage = computed(() => {
  return ['/login', '/register'].includes(route.path)
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <header v-if="!isAuthPage" class="bg-white shadow">
    <nav class="container mx-auto px-4 py-4 flex justify-between items-center">
      <div class="font-bold text-xl">AI Trip Planner</div>
      <div>
        <router-link to="/" class="mr-4 text-gray-600 hover:text-blue-500">首页</router-link>
        <router-link to="/chat" class="mr-4 text-gray-600 hover:text-blue-500">行程助手</router-link>
        <template v-if="!userStore.isLoggedIn">
          <router-link to="/login" class="mr-4 text-blue-500">登录</router-link>
          <router-link to="/register" class="bg-blue-500 text-white px-4 py-2 rounded">注册</router-link>
        </template>
        <template v-else>
          <span class="mr-4 text-gray-700">欢迎, {{ userStore.userInfo?.username || userStore.userInfo?.email }}</span>
          <button @click="handleLogout" class="text-red-500">退出</button>
        </template>
      </div>
    </nav>
  </header>
  <main>
    <RouterView />
  </main>
</template>

<style>
</style>
