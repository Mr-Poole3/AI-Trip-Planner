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
  <main class="min-h-screen bg-gray-50">
    <RouterView />
  </main>
</template>

<style>
</style>
