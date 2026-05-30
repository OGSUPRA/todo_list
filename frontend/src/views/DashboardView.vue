<template>
  <AppShell
    title="Панель задач с живым API"
    subtitle="Управляйте активными и выполненными задачами, сортируйте поток по приоритету и держите темп без перезагрузок."
  >
    <div class="stats fade-up">
      <section class="surface stat-card">
        <span>Всего задач</span>
        <strong>{{ summary.total }}</strong>
      </section>
      <section class="surface stat-card">
        <span>Активных</span>
        <strong>{{ summary.todo }}</strong>
      </section>
      <section class="surface stat-card">
        <span>Выполненных</span>
        <strong>{{ summary.done }}</strong>
      </section>
    </div>

    <div v-if="notice" class="notice success fade-up">{{ notice }}</div>

    <TaskComposer @create="createTask" @mark-all-done="markAllDone" />

    <TaskList
      :tasks="tasks"
      :meta="meta"
      :summary="summary"
      title="Актуальный список"
      heading-eyebrow="Ежедневный ритм"
      :search="filters.search"
      :status-filter="filters.status"
      :sort-by="filters.sort_by"
      :sort-order="filters.sort_order"
      :page-size="filters.page_size"
      empty-title="Пока пусто"
      empty-text="Добавьте первую задачу или измените фильтр, чтобы увидеть больше данных."
      @archive="archiveTask"
      @toggle="toggleTask"
      @update="updateTask"
      @search-change="onSearchChange"
      @status-change="onStatusChange"
      @sort-by-change="onSortByChange"
      @sort-order-change="onSortOrderChange"
      @page-change="onPageChange"
      @page-size-change="onPageSizeChange"
    />
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import TaskComposer from "@/components/TaskComposer.vue";
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
  sort_by: "created_at",
  sort_order: "desc",
});

async function fetchTasks() {
  const { data } = await api.get<TaskListResponse>("/tasks", {
    params: {
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

async function createTask(payload: { title: string; description: string }) {
  await api.post("/tasks", payload);
  notice.value = "Задача добавлена";
  filters.page = 1;
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

onMounted(() => {
  void fetchTasks();
});
</script>
