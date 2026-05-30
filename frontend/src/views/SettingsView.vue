<template>
  <AppShell
    title="Профиль и безопасность"
    subtitle="Управляйте своим аккаунтом, меняйте данные профиля, пароль и аватар без выхода из SPA."
  >
    <div class="settings-grid">
      <section class="surface card fade-up">
        <div class="eyebrow">Профиль</div>
        <h2>Основные данные</h2>
        <form class="grid" @submit.prevent="saveProfile">
          <div class="field">
            <label for="username">Имя пользователя</label>
            <input id="username" v-model="profile.username" class="input" type="text" required />
          </div>

          <div class="field">
            <label for="email">Email</label>
            <input id="email" v-model="profile.email" class="input" type="email" required />
          </div>

          <button class="btn" type="submit">Сохранить профиль</button>
        </form>
      </section>

      <section class="surface card fade-up">
        <div class="eyebrow">Аватар</div>
        <h2>Обновить изображение</h2>
        <form class="grid" @submit.prevent="uploadAvatar">
          <div class="field">
            <label for="avatar">Файл</label>
            <input id="avatar" ref="fileInput" class="input" type="file" accept=".png,.jpg,.jpeg,.webp" required />
          </div>

          <button class="btn secondary" type="submit">Загрузить аватар</button>
        </form>
      </section>

      <section class="surface card fade-up">
        <div class="eyebrow">Безопасность</div>
        <h2>Сменить пароль</h2>
        <form class="grid" @submit.prevent="changePassword">
          <div class="field">
            <label for="current-password">Текущий пароль</label>
            <input id="current-password" v-model="passwords.current_password" class="input" type="password" required />
          </div>

          <div class="field">
            <label for="new-password">Новый пароль</label>
            <input id="new-password" v-model="passwords.new_password" class="input" type="password" required />
          </div>

          <button class="btn secondary" type="submit">Обновить пароль</button>
        </form>
      </section>

      <section class="surface card fade-up">
        <div class="eyebrow">Удаление</div>
        <h2>Закрыть аккаунт</h2>
        <p class="subheadline small">Действие необратимо. После удаления вы сразу выйдете из системы.</p>
        <button class="btn danger" type="button" @click="deleteAccount">Удалить аккаунт</button>
      </section>
    </div>

    <div v-if="notice" class="notice success fade-up">{{ notice }}</div>
    <div v-if="error" class="notice error fade-up">{{ error }}</div>
  </AppShell>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import AppShell from "@/components/AppShell.vue";
import { api } from "@/lib/api";
import { clearAccessToken } from "@/lib/token";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const fileInput = ref<HTMLInputElement | null>(null);
const notice = ref("");
const error = ref("");

const profile = reactive({
  username: "",
  email: "",
});

const passwords = reactive({
  current_password: "",
  new_password: "",
});

watch(
  () => auth.user,
  (user) => {
    profile.username = user?.username ?? "";
    profile.email = user?.email ?? "";
  },
  { immediate: true },
);

async function saveProfile() {
  error.value = "";
  notice.value = "";
  try {
    await api.patch("/users/me", profile);
    await auth.fetchMe();
    notice.value = "Профиль обновлён";
  } catch {
    error.value = "Не удалось сохранить профиль";
  }
}

async function uploadAvatar() {
  error.value = "";
  notice.value = "";
  const file = fileInput.value?.files?.[0];
  if (!file) {
    error.value = "Выберите файл для загрузки";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  try {
    await api.post("/users/me/avatar", formData);
    await auth.fetchMe();
    notice.value = "Аватар обновлён";
  } catch {
    error.value = "Не удалось загрузить аватар";
  }
}

async function changePassword() {
  error.value = "";
  notice.value = "";
  try {
    await api.post("/users/me/password", passwords);
    await auth.logout();
    clearAccessToken();
    await router.push({ name: "login" });
  } catch {
    error.value = "Не удалось обновить пароль";
  }
}

async function deleteAccount() {
  error.value = "";
  notice.value = "";
  try {
    await api.delete("/users/me");
    await auth.logout();
    clearAccessToken();
    await router.push({ name: "login" });
  } catch {
    error.value = "Не удалось удалить аккаунт";
  }
}
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.72rem;
  color: #738194;
  margin-bottom: 10px;
}

h2 {
  margin: 0 0 18px;
}

.small {
  margin: 0 0 18px;
  font-size: 0.96rem;
}

@media (max-width: 960px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
