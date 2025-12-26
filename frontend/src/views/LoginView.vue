<template>
  <AuroraBackground>
    <div class="w-full max-w-md px-4 mx-auto">
      <!-- Logo & Header -->
      <div class="text-center mb-8 animate-fade-in">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-purple-600 text-white shadow-lg mb-4 transform hover:rotate-12 transition-transform duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">欢迎回来</h1>
        <p class="text-gray-500 mt-2">开启您的下一段精彩旅程</p>
      </div>

      <!-- Login Card -->
      <div class="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 animate-slide-up">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Email Field -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5 ml-1" for="email">电子邮箱</label>
            <div class="relative group">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400 group-focus-within:text-blue-500 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </span>
              <input
                v-model="form.email"
                class="block w-full pl-11 pr-4 py-3 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 shadow-sm"
                id="email"
                type="email"
                autocomplete="username"
                placeholder="name@example.com"
                required
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <div class="flex items-center justify-between mb-1.5 ml-1">
              <label class="text-sm font-semibold text-gray-700" for="password">登录密码</label>
              <a href="#" class="text-xs font-medium text-blue-600 hover:text-blue-500 transition-colors">忘记密码？</a>
            </div>
            <div class="relative group">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400 group-focus-within:text-blue-500 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </span>
              <input
                v-model="form.password"
                class="block w-full pl-11 pr-4 py-3 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 shadow-sm"
                id="password"
                type="password"
                autocomplete="current-password"
                placeholder="••••••••"
                required
                minlength="6"
                maxlength="72"
              />
            </div>
          </div>

          <!-- Remember Me -->
          <div class="flex items-center ml-1">
            <input id="remember-me" type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded-md transition-all">
            <label for="remember-me" class="ml-2 block text-sm text-gray-500 select-none">30天内自动登录</label>
          </div>

          <!-- Submit Button -->
          <button
            class="w-full relative group overflow-hidden bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3.5 rounded-2xl shadow-lg shadow-blue-500/30 transform transition-all duration-200 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
            type="submit"
            :disabled="loading"
          >
            <span class="relative z-10 flex items-center justify-center">
              <template v-if="loading">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                正在验证...
              </template>
              <template v-else>立即登录</template>
            </span>
          </button>

          <!-- Social Login Separator -->
          <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-3 bg-white/0 text-gray-400 font-medium">其他登录方式</span>
            </div>
          </div>

          <!-- Social Buttons -->
          <div class="grid grid-cols-2 gap-4">
            <button type="button" class="flex items-center justify-center py-2.5 px-4 bg-white/50 backdrop-blur-sm border border-gray-200 rounded-2xl hover:bg-gray-50/80 transition-all duration-200 shadow-sm group">
              <svg class="w-5 h-5 mr-2.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 12-4.53z" fill="#EA4335"/>
              </svg>
              <span class="text-sm font-semibold text-gray-700">Google</span>
            </button>
            <button type="button" class="flex items-center justify-center py-2.5 px-4 bg-white/50 backdrop-blur-sm border border-gray-200 rounded-2xl hover:bg-gray-50/80 transition-all duration-200 shadow-sm group">
              <svg class="w-5 h-5 mr-2.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 5.82 2 10.5c0 2.65 1.45 5.01 3.7 6.6l-.94 2.8c-.06.18.06.37.24.37.08 0 .15-.03.21-.08l3.41-2.05c.44.06.89.1 1.35.1 5.52 0 10-3.82 10-8.5S17.52 2 12 2zm3.82 10.64l-2.02-2.14c-.11-.12-.29-.12-.4 0l-1.6 1.7-2.66-2.82c-.11-.12-.29-.12-.4 0l-2.02 2.14c-.15.16-.04.42.18.42h8.74c.22 0 .33-.26.18-.42z" fill="#07C160"/>
              </svg>
              <span class="text-sm font-semibold text-gray-700">微信</span>
            </button>
          </div>
        </form>

        <!-- Footer Link -->
        <div class="mt-8 text-center">
          <p class="text-sm text-gray-500">
            还没有账号？
            <router-link to="/register" class="font-bold text-blue-600 hover:text-blue-700 transition-colors underline decoration-2 underline-offset-4">
              立即免费注册
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </AuroraBackground>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';
import AuroraBackground from '@/components/AuroraBackground.vue';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);

const form = reactive({
  email: '',
  password: '',
});

onMounted(() => {
  const autoFillData = sessionStorage.getItem('auto_fill_login');
  if (autoFillData) {
    try {
      const { email, password } = JSON.parse(autoFillData);
      if (email && password) {
        form.email = email;
        form.password = password;
        // 清除存储，防止刷新页面重复自动登录
        sessionStorage.removeItem('auto_fill_login');
        // 自动触发登录
        handleLogin();
      }
    } catch (e) {
      console.error('Auto fill error:', e);
      sessionStorage.removeItem('auto_fill_login');
    }
  }
});

const handleLogin = async () => {
  loading.value = true;
  try {
    const success = await userStore.login(form);
    if (success) {
      router.push('/');
    } else {
      // 可以在此处添加更优雅的错误提示组件
      alert('登录失败，请检查账号密码');
    }
  } catch (e: any) {
    console.error('Login error details:', e.response?.data);
    const errorMsg = e.response?.data?.detail?.[0]?.msg || e.message || '登录出错';
    alert(`登录失败: ${errorMsg}`);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

.animate-slide-up {
  animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
