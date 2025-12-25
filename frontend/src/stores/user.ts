import { defineStore } from 'pinia';
import request from '@/utils/request';

interface UserState {
  accessToken: string | null;
  refreshToken: string | null;
  userInfo: any | null;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    userInfo: JSON.parse(localStorage.getItem('user_info') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },
  actions: {
    async login(payload: any) {
      const res: any = await request.post('/auth/login', payload);
      if (res.code === 0) {
        this.setTokens(res.data);
        return true;
      }
      return false;
    },
    async register(payload: any) {
      const res: any = await request.post('/auth/register', payload);
      return res;
    },
    setTokens(data: any) {
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      this.userInfo = data.user;
      
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user_info', JSON.stringify(data.user));
    },
    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.userInfo = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_info');
    },
    async fetchUserInfo() {
        try {
            const res: any = await request.get('/auth/me');
            if(res.code === 0) {
                this.userInfo = res.data;
                localStorage.setItem('user_info', JSON.stringify(res.data));
            }
        } catch (e) {
            console.error(e);
        }
    }
  },
});
