<template>
  <AuroraBackground>
    <div class="w-full max-w-md px-4 py-8 mx-auto">
      <!-- Header -->
      <div class="text-center mb-8 animate-fade-in">
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">创建新账号</h1>
        <p class="text-gray-500 mt-2">加入我们，开始规划您的梦想之旅</p>
      </div>

      <!-- Register Card -->
      <div class="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 animate-slide-up">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <!-- Username Field -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5 ml-1" for="username">用户名</label>
            <div class="relative group">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400 group-focus-within:text-indigo-500 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              <input
                v-model="form.username"
                class="block w-full pl-11 pr-4 py-2.5 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 shadow-sm"
                id="username"
                type="text"
                autocomplete="username"
                placeholder="您的称呼"
                required
                minlength="2"
              />
            </div>
          </div>

          <!-- Email Field -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5 ml-1" for="email">电子邮箱</label>
            <div class="relative group">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400 group-focus-within:text-indigo-500 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </span>
              <input
                v-model="form.email"
                class="block w-full pl-11 pr-4 py-2.5 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 shadow-sm"
                id="email"
                type="email"
                autocomplete="email"
                placeholder="name@example.com"
                required
              />
            </div>
          </div>

          <!-- Password Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5 ml-1" for="password">密码</label>
              <input
                v-model="form.password"
                class="block w-full px-4 py-2.5 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 shadow-sm text-sm"
                id="password"
                type="password"
                autocomplete="new-password"
                placeholder="至少6位"
                required
                minlength="6"
                maxlength="72"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5 ml-1" for="confirm_password">确认密码</label>
              <input
                v-model="form.confirm_password"
                class="block w-full px-4 py-2.5 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 shadow-sm text-sm"
                id="confirm_password"
                type="password"
                autocomplete="new-password"
                placeholder="再次输入"
                required
                minlength="6"
                maxlength="72"
              />
            </div>
          </div>

          <!-- Captcha Field -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5 ml-1" for="captcha">验证码</label>
            <div class="flex space-x-3">
              <div class="relative flex-1 group">
                <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400 group-focus-within:text-indigo-500 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </span>
                <input
                  v-model="form.captcha"
                  class="block w-full pl-11 pr-4 py-2.5 bg-white/50 border border-gray-200 rounded-2xl leading-relaxed text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 shadow-sm"
                  id="captcha"
                  type="text"
                  placeholder="请输入6位验证码"
                  required
                />
              </div>
              <button
                type="button"
                @click="handleSendCode"
                :disabled="isSendingCode || countdown > 0"
                class="flex items-center justify-center px-4 min-w-[120px] bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100 font-semibold text-sm hover:bg-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="isSendingCode">发送中...</span>
                <span v-else-if="countdown > 0">{{ countdown }}s 后重发</span>
                <span v-else>获取验证码</span>
              </button>
            </div>
            <p class="text-[10px] text-gray-400 mt-1.5 ml-1">验证码将发送至您的邮箱</p>
          </div>

          <!-- Terms -->
          <div class="flex items-start ml-1 py-2">
            <input id="terms" type="checkbox" required class="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded-md transition-all">
            <label for="terms" class="ml-2 block text-xs text-gray-500 leading-normal">
              我已阅读并同意
              <a href="#" class="text-indigo-600 font-semibold hover:underline">服务协议</a> 和
              <a href="#" class="text-indigo-600 font-semibold hover:underline">隐私政策</a>
            </label>
          </div>

          <!-- Submit Button -->
          <button
            class="w-full relative group overflow-hidden bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3.5 rounded-2xl shadow-lg shadow-indigo-500/30 transform transition-all duration-200 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
            type="submit"
            :disabled="loading"
          >
            <span class="relative z-10 flex items-center justify-center">
              <template v-if="loading">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                正在创建...
              </template>
              <template v-else>开启旅程</template>
            </span>
          </button>
        </form>

        <!-- Footer Link -->
        <div class="mt-8 text-center border-t border-gray-100 pt-6">
          <p class="text-sm text-gray-500">
            已经有账号了？
            <router-link to="/login" class="font-bold text-indigo-600 hover:text-indigo-700 transition-colors underline decoration-2 underline-offset-4">
              点此登录
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </AuroraBackground>
</template>

<script setup lang="ts">
import { reactive, ref, onUnmounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';
import AuroraBackground from '@/components/AuroraBackground.vue';
import request from '@/utils/request';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);

// 验证码相关状态
const isSendingCode = ref(false);
const countdown = ref(0);
let timer: any = null;

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  captcha: '',
});

// 组件销毁时清理定时器
onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// 发送验证码逻辑
const handleSendCode = async () => {
  if (!form.email) {
    alert('请先输入电子邮箱');
    return;
  }

  // 简单的邮箱格式校验
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    alert('请输入有效的电子邮箱格式');
    return;
  }

  isSendingCode.value = true;
  try {
    const res: any = await request.post('/auth/send-code', {
      email: form.email,
      type: 'register'
    });

    // 如果请求成功（request.ts 拦截器会自动抛出非0 code 的错误）
    alert('验证码已发送，请查收邮件');
    startCountdown();
  } catch (e: any) {
    const errorMsg = e.response?.data?.message || e.message || '发送失败';
    alert(`发送失败: ${errorMsg}`);
  } finally {
    isSendingCode.value = false;
  }
};

// 倒计时逻辑
const startCountdown = () => {
  countdown.value = 60;
  timer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(timer);
    }
  }, 1000);
};

const handleRegister = async () => {
  if (form.password !== form.confirm_password) {
    alert('两次输入的密码不一致');
    return;
  }

  loading.value = true;
  try {
    const res: any = await userStore.register(form);
    if (res.code === 0) {
      alert('注册成功！正在跳转登录...');
      // 存储账号密码供登录页自动填充并登录
      sessionStorage.setItem('auto_fill_login', JSON.stringify({
        email: form.email,
        password: form.password
      }));
      router.push('/login');
    } else {
      alert(res.message || '注册失败');
    }
  } catch (e: any) {
    console.error('Registration error details:', e.response?.data);
    const errorMsg = e.response?.data?.detail?.[0]?.msg || e.message || '注册出错';
    alert(`注册失败: ${errorMsg}`);
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

/* 隐藏 Chrome 等浏览器的自动填充背景色 */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-box-shadow: 0 0 0px 1000px white inset !important;
  transition: background-color 5000s ease-in-out 0s;
}
</style>
