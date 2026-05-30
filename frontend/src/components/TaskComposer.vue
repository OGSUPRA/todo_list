<template>
  <section class="surface card fade-up">
    <div class="section-head">
      <div>
        <div class="eyebrow">Новая задача</div>
        <h2>Зафиксируйте то, что важно сейчас</h2>
      </div>
      <span class="badge">API-first workflow</span>
    </div>

    <form class="grid" @submit.prevent="submitTask">
      <div class="field">
        <label for="title">Название</label>
        <input id="title" v-model="form.title" class="input" type="text" maxlength="180" required />
      </div>

      <div class="field">
        <label for="description">Описание</label>
        <textarea id="description" v-model="form.description" class="textarea" maxlength="5000" />
      </div>

      <div class="inline-actions">
        <button class="btn" type="submit">Добавить задачу</button>
        <button class="btn secondary" type="button" @click="emit('mark-all-done')">
          Закрыть все активные
        </button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { reactive } from "vue";

const emit = defineEmits<{
  create: [payload: { title: string; description: string }];
  "mark-all-done": [];
}>();

const form = reactive({
  title: "",
  description: "",
});

function submitTask() {
  emit("create", { ...form });
  form.title = "";
  form.description = "";
}
</script>

<style scoped>
.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
}

.section-head h2 {
  margin: 0;
  font-size: 1.35rem;
}

.badge,
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.72rem;
  color: #738194;
}

.badge {
  padding: 10px 12px;
  border-radius: 999px;
  background: rgba(19, 34, 56, 0.06);
}
</style>
