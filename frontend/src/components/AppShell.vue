<template>
  <div class="page-shell">
    <div class="shell-grid">
      <header class="hero surface card fade-up">
        <div>
          <div class="eyebrow">Todo Product</div>
          <h1 class="headline">{{ title }}</h1>
          <p class="subheadline">{{ subtitle }}</p>
        </div>
        <aside class="profile-tile">
          <div class="profile-orb">
            <img v-if="user?.avatar_path" :src="user.avatar_path" alt="Аватар" />
            <span v-else>{{ initials }}</span>
          </div>
          <div>
            <div class="eyebrow">Ваш аккаунт</div>
            <div class="profile-headline">
              <strong>{{ user?.username }}</strong>
              <span v-if="user" class="role-pill" :class="user.role">{{ roleLabel(user.role) }}</span>
            </div>
            <div class="muted">{{ user?.email }}</div>
          </div>
        </aside>
      </header>

      <nav class="toolbar surface card fade-up">
        <RouterLink class="nav-link" to="/">Задачи</RouterLink>
        <RouterLink class="nav-link" to="/archived">Архив</RouterLink>
        <RouterLink class="nav-link" to="/settings">Профиль</RouterLink>
        <RouterLink v-if="auth.isAdmin" class="nav-link" to="/admin">Админка</RouterLink>
        <button class="btn ghost" type="button" @click="onLogout">Выйти</button>
      </nav>

      <main class="content-grid">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const props = defineProps<{
  title: string;
  subtitle: string;
}>();

const auth = useAuthStore();
const router = useRouter();
const user = computed(() => auth.user);
const initials = computed(() => auth.user?.username.slice(0, 2).toUpperCase() ?? "?");

async function onLogout() {
  await auth.logout();
  await router.push({ name: "login" });
}

function roleLabel(role: string) {
  return {
    admin: "Admin",
    vip: "VIP",
    standard: "Standart",
  }[role] ?? role;
}
</script>

<style scoped>
.shell-grid {
  display: grid;
  gap: 18px;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.nav-link {
  padding: 12px 14px;
  border-radius: 14px;
  color: #425064;
  font-weight: 600;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-link.router-link-active {
  background: #132238;
  color: #fff6e7;
}

.profile-tile {
  min-width: 250px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-headline {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.profile-orb {
  width: 72px;
  height: 72px;
  border-radius: 24px;
  background:
    linear-gradient(135deg, #132238 0%, #4f6f9a 100%);
  color: #fff6e7;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 700;
  overflow: hidden;
}

.profile-orb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.73rem;
  color: #738194;
  margin-bottom: 10px;
}

.muted {
  color: #647284;
  margin-top: 4px;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.role-pill.admin {
  background: rgba(185, 61, 47, 0.12);
  color: #7f2418;
}

.role-pill.vip {
  background: rgba(166, 120, 23, 0.12);
  color: #8a6113;
}

.role-pill.standard {
  background: rgba(45, 94, 195, 0.12);
  color: #264f9f;
}

.content-grid {
  display: grid;
  gap: 18px;
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
  }

  .profile-tile {
    min-width: auto;
  }
}
</style>
