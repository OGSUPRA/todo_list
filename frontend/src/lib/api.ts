import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/token";
import type { TokenResponse } from "@/types";

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

const baseURL = "/api/v1";

export const publicApi = axios.create({
  baseURL,
  withCredentials: true,
});

export const api = axios.create({
  baseURL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshRequest: Promise<string> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const responseStatus = error.response?.status;
    const config = error.config as RetriableConfig | undefined;

    if (responseStatus !== 401 || !config || config._retry || config.url?.includes("/auth/")) {
      return Promise.reject(error);
    }

    config._retry = true;

    if (!refreshRequest) {
      refreshRequest = publicApi
        .post<TokenResponse>("/auth/refresh")
        .then(({ data }) => {
          setAccessToken(data.access_token);
          return data.access_token;
        })
        .catch((refreshError) => {
          clearAccessToken();
          throw refreshError;
        })
        .finally(() => {
          refreshRequest = null;
        });
    }

    const freshToken = await refreshRequest;
    config.headers.Authorization = `Bearer ${freshToken}`;
    return api.request(config);
  },
);
