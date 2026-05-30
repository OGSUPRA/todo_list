<template>
  <AppShell
    title="Архив без потерь"
    subtitle="Удаление стало мягким: задачи можно вернуть в рабочий поток в любой момент через API."
  >
    <div v-if="notice" class="notice info fade-up">{{ notice }}</div>

    <TaskList
      :tasks="tasks"
      title="Архивированные задачи"
      heading-eyebrow="Мягкое удаление"
      :search="search"
      :status-filter="statusFilter"
      @restore="restoreTask"
      @toggle="toggleTask"
      @update="updateTask"
      @search-change="onSearchChange"
      @status-change="onStatusChange"
      @archive="noop"
    />
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import TaskList from "@/components/TaskList.vue";
import { api } from "@/lib/api";
import type { Task } from "@/types";

const tasks = ref<Task[]>([]);
const notice = ref("");
const search = ref("");
const statusFilter = ref("");

async function fetchTasks() {
  const { data } = await api.get<Task[]>("/tasks", {
    params: {
      include_deleted: true,
      search: search.value || undefined,
      status: statusFilter.value || undefined,
    },
  });
  tasks.value = data.filter((task) => task.is_deleted);
}

async function restoreTask(taskId: string) {
  await api.post(`/tasks/${taskId}/restore`);
  notice.value = "Задача возвращена из архива";
  await fetchTasks();
}

async function updateTask(taskId: string, payload: { title: string; description: string }) {
  await api.patch(`/tasks/${taskId}`, payload);
  await fetchTasks();
}

async function toggleTask(taskId: string) {
  await api.post(`/tasks/${taskId}/toggle`);
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

function noop() {
  return undefined;
}

onMounted(() => {
  void fetchTasks();
});
</script>
