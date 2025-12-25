import axios from 'axios';
import { useUserStore } from '@/stores/user';

const request = axios.create({
  baseURL: 'http://localhost:9000/api/v1', // 确保这个前缀与后端路由匹配
  timeout: 10000,
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    if (userStore.accessToken) {
      config.headers.Authorization = `Bearer ${userStore.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data;
    // 如果后端返回 code 字段，可以在这里做统一处理
    if (res.code !== undefined && res.code !== 0) {
      // 处理特定错误，例如 1003 Token 过期，可以在这里尝试刷新或跳转登录
      return Promise.reject(new Error(res.message || 'Error'));
    }
    return res;
  },
  async (error) => {
    const userStore = useUserStore();
    if (error.response) {
      const { status } = error.response;
      if (status === 401) {
        // Token 过期或无效
        // 尝试刷新 token (略，简化处理直接退出)
        userStore.logout();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default request;
