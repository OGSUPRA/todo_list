<template>
  <div class="auth-layout">
    <section class="auth-panel surface card fade-up">
      <div class="eyebrow">Todo Product</div>
      <h1 class="headline">Вход без трения, фокус на работе</h1>
      <p class="subheadline">
        Новый стек уже под капотом: FastAPI, PostgreSQL, JWT и отдельный Vue 3 фронтенд.
      </p>

      <form class="grid" @submit.prevent="submit">
        <div class="field">
          <label for="login">Логин или email</label>
          <input id="login" v-model="form.username" class="input" type="text" required />
        </div>

        <div class="field">
          <label for="password">Пароль</label>
          <input id="password" v-model="form.password" class="input" type="password" required />
        </div>

        <div v-if="error" class="notice error">{{ error }}</div>

        <div class="inline-actions">
          <button class="btn" type="submit">Войти</button>
          <RouterLink class="btn ghost" to="/register">Регистрация</RouterLink>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const error = ref("");
const form = reactive({
  username: "",
  password: "",
});

async function submit() {
  error.value = "";
  try {
    await auth.login(form);
    await router.push({ name: "dashboard" });
  } catch (err) {
    error.value = "Не удалось войти. Проверьте логин и пароль.";
  }
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.auth-panel {
  width: min(100%, 620px);
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.72rem;
  color: #738194;
  margin-bottom: 10px;
}
</style>
