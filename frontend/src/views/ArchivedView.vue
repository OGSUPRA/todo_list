<template>
  <AppShell
    title="Архив без потерь"
    subtitle="Удаление стало мягким: архив тоже сортируется, фильтруется и возвращает задачи в рабочий поток без ручного поиска."
  >
    <div v-if="notice" class="notice info fade-up">{{ notice }}</div>

    <TaskList
      :tasks="tasks"
      :meta="meta"
      :summary="summary"
      title="Архивированные задачи"
      heading-eyebrow="Мягкое удаление"
      :search="filters.search"
      :status-filter="filters.status"
      :sort-by="filters.sort_by"
      :sort-order="filters.sort_order"
      :page-size="filters.page_size"
      empty-title="Архив пока пуст"
      empty-text="Сейчас здесь ничего нет. Когда отправите задачу в архив, она появится на этой странице."
      @restore="restoreTask"
      @toggle="toggleTask"
      @update="updateTask"
      @search-change="onSearchChange"
      @status-change="onStatusChange"
      @sort-by-change="onSortByChange"
      @sort-order-change="onSortOrderChange"
      @page-change="onPageChange"
      @page-size-change="onPageSizeChange"
      @archive="noop"
    />
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import TaskList from "@/components/TaskList.vue";
import { api } from "@/lib/api";
import type { PaginationMeta, Task, TaskListResponse, TaskSummary } from "@/types";

const tasks = ref<Task[]>([]);
const notice = ref("");
const meta = ref<PaginationMeta | null>(null);
const summary = ref<TaskSummary>({
  total: 0,
  todo: 0,
  done: 0,
  archived: 0,
});

const filters = reactive({
  search: "",
  status: "",
  page: 1,
  page_size: 10,
  sort_by: "updated_at",
  sort_order: "desc",
});

async function fetchTasks() {
  const { data } = await api.get<TaskListResponse>("/tasks", {
    params: {
      only_deleted: true,
      search: filters.search || undefined,
      status: filters.status || undefined,
      page: filters.page,
      page_size: filters.page_size,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    },
  });
  tasks.value = data.items;
  meta.value = data.meta;
  summary.value = data.summary;
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

function resetPage() {
  filters.page = 1;
}

function onSearchChange(value: string) {
  filters.search = value;
  resetPage();
  void fetchTasks();
}

function onStatusChange(value: string) {
  filters.status = value;
  resetPage();
  void fetchTasks();
}

function onSortByChange(value: string) {
  filters.sort_by = value;
  resetPage();
  void fetchTasks();
}

function onSortOrderChange(value: string) {
  filters.sort_order = value;
  resetPage();
  void fetchTasks();
}

function onPageChange(value: number) {
  filters.page = value;
  void fetchTasks();
}

function onPageSizeChange(value: number) {
  filters.page_size = value;
  resetPage();
  void fetchTasks();
}

function noop() {
  return undefined;
}

onMounted(() => {
  void fetchTasks();
});
</script>
