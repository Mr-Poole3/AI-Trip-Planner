<script setup lang="ts">
import { useRouter } from 'vue-router';
import AuroraBackground from '../components/AuroraBackground.vue';
import {
  Map,
  Calendar,
  Sparkles,
  Globe,
  Clock,
  Shield,
  Menu,
  X,
  ChevronRight,
  Plane,
  Hotel,
  Utensils,
  Camera,
  Wallet,
  CloudSun
} from 'lucide-vue-next';
import { ref } from 'vue';

const router = useRouter();
const isMobileMenuOpen = ref(false);

const startJourney = () => {
  router.push('/chat');
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const features = [
  {
    icon: Sparkles,
    title: 'AI 智能规划',
    description: '基于先进的大语言模型，为您量身定制最符合您偏好的旅行路线。'
  },
  {
    icon: Clock,
    title: '实时动态调整',
    description: '无论天气突变还是临时起意，行程安排随时随地灵活调整。'
  },
  {
    icon: Globe,
    title: '全球覆盖',
    description: '支持全球 200+ 国家和地区的旅行规划，无论去哪，都能为您导航。'
  },
  {
    icon: Wallet,
    title: '智能预算控制',
    description: '根据您的预算范围，自动推荐性价比最高的交通、住宿和餐饮方案。'
  },
  {
    icon: Camera,
    title: '小众景点发掘',
    description: '避开人挤人的热门打卡地，带您探索鲜为人知的本地宝藏景点。'
  },
  {
    icon: CloudSun,
    title: '天气智能避险',
    description: '自动监测目的地天气，遇到恶劣天气时主动建议室内替代行程。'
  }
];

const steps = [
  {
    id: 1,
    title: '告诉我们您的想法',
    desc: '输入目的地、时间、预算和兴趣偏好。'
  },
  {
    id: 2,
    title: 'AI 生成方案',
    desc: '几秒钟内，为您生成包含景点、美食和住宿的完整行程。'
  },
  {
    id: 3,
    title: '自由调整',
    desc: '对行程不满意？随时与 AI 对话修改细节。'
  }
];
</script>

<template>
  <div class="min-h-screen bg-white font-sans text-slate-900 selection:bg-blue-100">
    <!-- Navbar -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center gap-2 cursor-pointer" @click="router.push('/')">
            <div class="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white">
              <Plane class="w-5 h-5" />
            </div>
            <span class="font-bold text-xl tracking-tight">AI Trip Planner</span>
          </div>

          <!-- Desktop Menu -->
          <div class="hidden md:flex items-center space-x-8">
            <a href="#features" class="text-slate-600 hover:text-black transition-colors text-sm font-medium">功能特点</a>
            <a href="#how-it-works" class="text-slate-600 hover:text-black transition-colors text-sm font-medium">如何使用</a>
            <a href="#" class="text-slate-600 hover:text-black transition-colors text-sm font-medium">关于我们</a>
            <button @click="startJourney" class="bg-black text-white px-5 py-2 rounded-full text-sm font-medium hover:bg-neutral-800 transition-colors shadow-sm">
              开始规划
            </button>
          </div>

          <!-- Mobile Menu Button -->
          <div class="md:hidden flex items-center">
            <button @click="toggleMobileMenu" class="text-slate-600 hover:text-black focus:outline-none">
              <Menu v-if="!isMobileMenuOpen" class="w-6 h-6" />
              <X v-else class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Menu Dropdown -->
      <div v-if="isMobileMenuOpen" class="md:hidden bg-white border-b border-slate-100">
        <div class="px-4 pt-2 pb-4 space-y-1">
          <a href="#features" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:text-black hover:bg-slate-50">功能特点</a>
          <a href="#how-it-works" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:text-black hover:bg-slate-50">如何使用</a>
          <button @click="startJourney" class="w-full mt-4 bg-black text-white px-5 py-3 rounded-lg text-base font-medium hover:bg-neutral-800 transition-colors">
            开始规划
          </button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <AuroraBackground>
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 md:pt-32 md:pb-24 flex flex-col items-center text-center">

        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-xs font-semibold mb-8 animate-fade-in-up">
          <Sparkles class="w-3 h-3" />
          <span>全新 AI 引擎升级</span>
        </div>

        <!-- Heading -->
        <h1 class="text-5xl md:text-7xl font-bold tracking-tight text-slate-900 mb-6 max-w-4xl leading-tight">
          下一站旅行，<br/>
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-violet-600">由 AI 为您完美定制</span>
        </h1>

        <!-- Subheading -->
        <p class="mt-4 text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed mb-10">
          告别繁琐的攻略查询。只需告诉我们需要什么，剩下的交给智能算法。
          <br class="hidden md:block"/>从行程规划到酒店预订，一站式搞定。
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          <button
            @click="startJourney"
            class="px-8 py-4 rounded-full bg-black text-white hover:bg-neutral-800 font-semibold text-lg transition-all duration-200 shadow-xl hover:shadow-2xl flex items-center justify-center gap-2 group"
          >
            立即开始
            <ChevronRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button class="px-8 py-4 rounded-full bg-white text-slate-900 border border-slate-200 hover:bg-slate-50 font-semibold text-lg transition-all duration-200 shadow-sm hover:shadow-md">
            观看演示
          </button>
        </div>

        <!-- Visual Mockup (Floating Cards) -->
        <div class="mt-20 relative w-full max-w-5xl mx-auto hidden md:block h-[400px]">
          <!-- Card 1: Chat Interface -->
          <div class="absolute left-1/2 -translate-x-1/2 top-0 w-[500px] bg-white rounded-2xl shadow-2xl border border-slate-100 p-4 z-20 transform hover:-translate-y-2 transition-transform duration-500">
            <div class="flex items-center gap-2 mb-4 border-b border-slate-50 pb-3">
              <div class="w-3 h-3 rounded-full bg-red-400"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div class="w-3 h-3 rounded-full bg-green-400"></div>
              <div class="ml-auto text-xs text-slate-400">AI Assistant</div>
            </div>
            <div class="space-y-3">
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                  <Plane class="w-4 h-4" />
                </div>
                <div class="bg-slate-50 p-3 rounded-2xl rounded-tl-none text-sm text-slate-600 max-w-[80%]">
                  我想去日本玩 7 天，预算 2 万，喜欢动漫和美食，请帮我规划一下。
                </div>
              </div>
              <div class="flex gap-3 flex-row-reverse">
                 <div class="w-8 h-8 rounded-full bg-black flex items-center justify-center text-white">
                  <Sparkles class="w-4 h-4" />
                </div>
                <div class="bg-blue-50 p-3 rounded-2xl rounded-tr-none text-sm text-slate-800 max-w-[90%] shadow-sm">
                  <p class="font-medium mb-1">已为您生成日本 7 日游方案 🇯🇵</p>
                  <ul class="list-disc list-inside space-y-1 text-xs text-slate-600">
                    <li>Day 1: 东京 - 秋叶原动漫巡礼</li>
                    <li>Day 2: 筑地市场海鲜 & 浅草寺</li>
                    <li>Day 3: 新宿 & 涩谷购物</li>
                    <li>...</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Card 2: Hotel Info (Left) -->
          <div class="absolute left-0 top-20 w-[280px] bg-white rounded-xl shadow-xl border border-slate-100 p-4 z-10 transform -rotate-6 hover:rotate-0 transition-transform duration-500">
            <div class="flex gap-3 mb-3">
              <div class="w-12 h-12 bg-slate-200 rounded-lg overflow-hidden relative">
                 <Hotel class="w-full h-full p-2 text-slate-400" />
              </div>
              <div>
                <div class="font-bold text-sm">东京安达仕酒店</div>
                <div class="text-xs text-slate-500">Minato-ku, Tokyo</div>
              </div>
            </div>
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">已预订</span>
              <span class="text-sm font-bold">¥3,200/晚</span>
            </div>
          </div>

          <!-- Card 3: Food Info (Right) -->
          <div class="absolute right-0 top-32 w-[260px] bg-white rounded-xl shadow-xl border border-slate-100 p-4 z-10 transform rotate-3 hover:rotate-0 transition-transform duration-500">
             <div class="flex items-center gap-3 mb-2">
               <div class="p-2 bg-orange-100 rounded-lg text-orange-600">
                 <Utensils class="w-5 h-5" />
               </div>
               <div class="font-bold text-sm">推荐餐厅</div>
             </div>
             <div class="text-sm text-slate-700 mb-2">数寄屋桥次郎</div>
             <div class="w-full bg-slate-100 rounded-full h-1.5 mb-1">
               <div class="bg-orange-400 h-1.5 rounded-full" style="width: 90%"></div>
             </div>
             <div class="text-xs text-slate-400 flex justify-between">
               <span>匹配度</span>
               <span>98%</span>
             </div>
          </div>
        </div>

      </div>
    </AuroraBackground>

    <!-- Features Section -->
    <section id="features" class="py-24 bg-white relative">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-base font-semibold text-blue-600 tracking-wide uppercase">核心功能</h2>
          <p class="mt-2 text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">
            重新定义您的旅行规划体验
          </p>
          <p class="mt-4 text-xl text-slate-500">
            不仅仅是简单的行程罗列，而是基于人工智能的智能旅行助手。
          </p>
        </div>

        <div class="relative w-full overflow-hidden group">
          <!-- Left fade overlay -->
          <div class="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none"></div>
          <!-- Right fade overlay -->
          <div class="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none"></div>

          <!-- Marquee Container -->
          <div class="flex overflow-hidden">
             <div class="flex gap-8 py-8 animate-marquee hover:pause-animation">
               <!-- Original set -->
               <div v-for="feature in features" :key="feature.title" class="flex-none w-80 group/card relative p-8 bg-slate-50 rounded-3xl hover:bg-blue-50/50 transition-colors duration-300 border border-slate-100">
                 <div class="absolute top-8 left-8 p-3 bg-white rounded-2xl shadow-sm ring-1 ring-slate-900/5 group-hover/card:scale-110 transition-transform duration-300">
                   <component :is="feature.icon" class="h-6 w-6 text-blue-600" />
                 </div>
                 <h3 class="mt-16 text-xl font-bold text-slate-900">{{ feature.title }}</h3>
                 <p class="mt-4 text-base text-slate-600 leading-relaxed">
                   {{ feature.description }}
                 </p>
               </div>

               <!-- Duplicate set for seamless scrolling -->
               <div v-for="feature in features" :key="feature.title + '-duplicate'" class="flex-none w-80 group/card relative p-8 bg-slate-50 rounded-3xl hover:bg-blue-50/50 transition-colors duration-300 border border-slate-100">
                 <div class="absolute top-8 left-8 p-3 bg-white rounded-2xl shadow-sm ring-1 ring-slate-900/5 group-hover/card:scale-110 transition-transform duration-300">
                   <component :is="feature.icon" class="h-6 w-6 text-blue-600" />
                 </div>
                 <h3 class="mt-16 text-xl font-bold text-slate-900">{{ feature.title }}</h3>
                 <p class="mt-4 text-base text-slate-600 leading-relaxed">
                   {{ feature.description }}
                 </p>
               </div>
             </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-24 bg-slate-50 border-t border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 class="text-3xl font-bold text-slate-900 mb-6">只需三步，<br/>开启您的梦幻之旅</h2>
            <div class="space-y-8">
              <div v-for="step in steps" :key="step.id" class="flex gap-4">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold shadow-lg shadow-blue-200">
                  {{ step.id }}
                </div>
                <div>
                  <h3 class="text-lg font-bold text-slate-900 mb-1">{{ step.title }}</h3>
                  <p class="text-slate-600">{{ step.desc }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="relative">
             <div class="absolute inset-0 bg-gradient-to-tr from-blue-200 to-violet-200 rounded-3xl transform rotate-3 blur-sm opacity-50"></div>
             <div class="relative bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                <!-- Decorative map placeholder -->
                <div class="aspect-video bg-slate-100 rounded-xl overflow-hidden relative group">
                  <img
                    src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
                    alt="Travel Planning Map"
                    class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div class="absolute inset-0 bg-black/10 group-hover:bg-black/0 transition-colors duration-500"></div>

                  <!-- UI Overlay mimicking a map interface -->
                  <div class="absolute top-4 right-4 bg-white/90 backdrop-blur-sm p-2 rounded-lg shadow-sm">
                    <Map class="w-5 h-5 text-blue-600" />
                  </div>

                  <!-- Location markers simulation -->
                  <div class="absolute top-1/3 left-1/4 w-4 h-4 bg-blue-500 border-2 border-white rounded-full shadow-lg animate-bounce"></div>
                  <div class="absolute top-1/2 right-1/3 w-4 h-4 bg-red-500 border-2 border-white rounded-full shadow-lg animate-bounce" style="animation-delay: 0.5s"></div>

                  <!-- Route line simulation -->
                  <svg class="absolute inset-0 w-full h-full pointer-events-none" style="filter: drop-shadow(0 2px 2px rgba(0,0,0,0.3));">
                    <path d="M150 120 Q 300 150 400 180" stroke="white" stroke-width="2" fill="none" stroke-dasharray="4 4" class="opacity-80" />
                  </svg>
                </div>

                <div class="mt-6 flex justify-between items-center">
                   <div class="flex -space-x-2">
                      <img class="w-8 h-8 rounded-full border-2 border-white object-cover" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=64&h=64" alt="User" />
                      <img class="w-8 h-8 rounded-full border-2 border-white object-cover" src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=64&h=64" alt="User" />
                      <img class="w-8 h-8 rounded-full border-2 border-white object-cover" src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=64&h=64" alt="User" />
                      <div class="w-8 h-8 rounded-full bg-slate-800 border-2 border-white flex items-center justify-center text-[10px] text-white font-bold">+2k</div>
                   </div>
                   <div class="text-sm font-medium text-slate-500">已被 2,000+ 旅行者选择</div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          <div class="col-span-2 md:col-span-1">
             <div class="flex items-center gap-2 mb-4">
               <div class="w-6 h-6 bg-black rounded-md flex items-center justify-center text-white">
                 <Plane class="w-3 h-3" />
               </div>
               <span class="font-bold text-lg">AI Trip Planner</span>
             </div>
             <p class="text-sm text-slate-500 max-w-xs">
               利用人工智能技术，为每个人提供私人定制的旅行体验。
             </p>
          </div>
          <div>
            <h4 class="font-bold text-slate-900 mb-4">产品</h4>
            <ul class="space-y-2 text-sm text-slate-600">
              <li><a href="#" class="hover:text-blue-600">功能介绍</a></li>
              <li><a href="#" class="hover:text-blue-600">定价方案</a></li>
              <li><a href="#" class="hover:text-blue-600">API 接口</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-bold text-slate-900 mb-4">公司</h4>
            <ul class="space-y-2 text-sm text-slate-600">
              <li><a href="#" class="hover:text-blue-600">关于我们</a></li>
              <li><a href="#" class="hover:text-blue-600">加入我们</a></li>
              <li><a href="#" class="hover:text-blue-600">联系方式</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-bold text-slate-900 mb-4">法律</h4>
            <ul class="space-y-2 text-sm text-slate-600">
              <li><a href="#" class="hover:text-blue-600">隐私政策</a></li>
              <li><a href="#" class="hover:text-blue-600">服务条款</a></li>
            </ul>
          </div>
        </div>
        <div class="pt-8 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
          <p class="text-sm text-slate-400">© 2024 AI Trip Planner. All rights reserved.</p>
          <div class="flex gap-4">
            <!-- Social Icons placeholders -->
            <div class="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 hover:bg-slate-200 cursor-pointer">
              <span class="sr-only">Twitter</span>
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path></svg>
            </div>
            <div class="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 hover:bg-slate-200 cursor-pointer">
              <span class="sr-only">GitHub</span>
               <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 7.15 9.6.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.1-1.46-1.1-1.46-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.1.39-2 1.03-2.71-.1-.25-.45-1.28.1-2.67 0 0 .84-.27 2.75 1.02a9.6 9.6 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.39.2 2.42.1 2.67.64.71 1.03 1.61 1.03 2.71 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.75c0 .26.18.57.69.48C21.13 20.18 24 16.42 24 12c0-5.52-4.48-10-10-10z"></path></svg>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Custom animations if needed */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-marquee {
  animation: marquee 40s linear infinite;
}

.hover\:pause-animation:hover {
  animation-play-state: paused;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* Hide scrollbar for Chrome, Safari and Opera */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.hide-scrollbar {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
</style>
