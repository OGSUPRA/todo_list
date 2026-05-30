import { defineStore } from "pinia";

import { api, publicApi } from "@/lib/api";
import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/token";
import type { LoginPayload, RegisterPayload, TokenResponse, User } from "@/types";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    ready: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user && getAccessToken()),
  },
  actions: {
    async bootstrap() {
      if (this.ready) {
        return;
      }

      const token = getAccessToken();
      if (token) {
        try {
          await this.fetchMe();
          this.ready = true;
          return;
        } catch {
          clearAccessToken();
        }
      }

      try {
        const { data } = await publicApi.post<TokenResponse>("/auth/refresh");
        setAccessToken(data.access_token);
        await this.fetchMe();
      } catch {
        clearAccessToken();
        this.user = null;
      } finally {
        this.ready = true;
      }
    },

    async register(payload: RegisterPayload) {
      await publicApi.post("/auth/register", payload);
      await this.login({ username: payload.username, password: payload.password });
    },

    async login(payload: LoginPayload) {
      const { data } = await publicApi.post<TokenResponse>("/auth/login", payload);
      setAccessToken(data.access_token);
      await this.fetchMe();
    },

    async fetchMe() {
      const { data } = await api.get<User>("/users/me");
      this.user = data;
    },

    async logout() {
      try {
        await api.post("/auth/logout");
      } finally {
        clearAccessToken();
        this.user = null;
      }
    },
  },
});
