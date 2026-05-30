<template>
  <AppShell
    title="Панель задач с живым API"
    subtitle="Управляйте активными и выполненными задачами, не перезагружая страницу и не касаясь серверных шаблонов."
  >
    <div class="stats fade-up">
      <section class="surface stat-card">
        <span>Всего задач</span>
        <strong>{{ tasks.length }}</strong>
      </section>
      <section class="surface stat-card">
        <span>Активных</span>
        <strong>{{ todoCount }}</strong>
      </section>
      <section class="surface stat-card">
        <span>Выполненных</span>
        <strong>{{ doneCount }}</strong>
      </section>
    </div>

    <div v-if="notice" class="notice success fade-up">{{ notice }}</div>

    <TaskComposer @create="createTask" @mark-all-done="markAllDone" />

    <TaskList
      :tasks="tasks"
      title="Актуальный список"
      heading-eyebrow="Ежедневный ритм"
      :search="search"
      :status-filter="statusFilter"
      @archive="archiveTask"
      @toggle="toggleTask"
      @update="updateTask"
      @search-change="onSearchChange"
      @status-change="onStatusChange"
    />
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import TaskComposer from "@/components/TaskComposer.vue";
import TaskList from "@/components/TaskList.vue";
import { api } from "@/lib/api";
import type { Task } from "@/types";

const tasks = ref<Task[]>([]);
const notice = ref("");
const search = ref("");
const statusFilter = ref("");

const todoCount = computed(() => tasks.value.filter((task) => task.status === "todo").length);
const doneCount = computed(() => tasks.value.filter((task) => task.status === "done").length);

async function fetchTasks() {
  const { data } = await api.get<Task[]>("/tasks", {
    params: {
      search: search.value || undefined,
      status: statusFilter.value || undefined,
    },
  });
  tasks.value = data;
}

async function createTask(payload: { title: string; description: string }) {
  await api.post("/tasks", payload);
  notice.value = "Задача добавлена";
  await fetchTasks();
}

async function toggleTask(taskId: string) {
  await api.post(`/tasks/${taskId}/toggle`);
  await fetchTasks();
}

async function updateTask(taskId: string, payload: { title: string; description: string }) {
  await api.patch(`/tasks/${taskId}`, payload);
  notice.value = "Изменения сохранены";
  await fetchTasks();
}

async function archiveTask(taskId: string) {
  await api.delete(`/tasks/${taskId}`);
  notice.value = "Задача перенесена в архив";
  await fetchTasks();
}

async function markAllDone() {
  await api.post("/tasks/mark-all-done");
  notice.value = "Все активные задачи закрыты";
  await fetchTasks();
}

function onSearchChange(value: string) {
  search.value = value;
  void fetchTasks();
}

function onStatusChange(value: string) {
  statusFilter.value = value;
  void fetchTasks();
}

onMounted(() => {
  void fetchTasks();
});
</script>
