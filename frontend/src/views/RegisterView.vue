<template>
  <div class="auth-layout">
    <section class="auth-panel surface card fade-up">
      <div class="eyebrow">Новый аккаунт</div>
      <h1 class="headline">Соберите своё пространство задач</h1>
      <p class="subheadline">
        Регистрация теперь сразу создаёт пользователя в PostgreSQL и открывает SPA без серверных шаблонов.
      </p>

      <form class="grid" @submit.prevent="submit">
        <div class="field">
          <label for="username">Имя пользователя</label>
          <input id="username" v-model="form.username" class="input" type="text" required />
        </div>

        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" class="input" type="email" required />
        </div>

        <div class="field">
          <label for="password">Пароль</label>
          <input id="password" v-model="form.password" class="input" type="password" required />
        </div>

        <div v-if="error" class="notice error">{{ error }}</div>

        <div class="inline-actions">
          <button class="btn" type="submit">Создать аккаунт</button>
          <RouterLink class="btn ghost" to="/login">Назад ко входу</RouterLink>
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
  email: "",
  password: "",
});

async function submit() {
  error.value = "";
  try {
    await auth.register(form);
    await router.push({ name: "dashboard" });
  } catch {
    error.value = "Не удалось зарегистрироваться. Возможно, логин или email уже заняты.";
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
