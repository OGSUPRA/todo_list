<template>
  <section class="surface card fade-up">
    <div class="section-head">
      <div>
        <div class="eyebrow">{{ headingEyebrow }}</div>
        <h2>{{ title }}</h2>
        <p v-if="summary" class="summary-line">
          Всего: {{ summary.total }} · Активных: {{ summary.todo }} · Выполненных: {{ summary.done }} · В архиве:
          {{ summary.archived }}
        </p>
      </div>

      <div class="filters">
        <input
          v-model="localSearch"
          class="input compact"
          type="search"
          placeholder="Поиск по названию и описанию"
          @input="emit('search-change', localSearch)"
        />
        <select v-model="localStatus" class="select compact" @change="emit('status-change', localStatus)">
          <option value="">Все статусы</option>
          <option value="todo">Только активные</option>
          <option value="done">Только выполненные</option>
        </select>
        <select v-model="localSortBy" class="select compact" @change="emit('sort-by-change', localSortBy)">
          <option value="created_at">По дате создания</option>
          <option value="updated_at">По обновлению</option>
          <option value="title">По названию</option>
          <option value="status">По статусу</option>
        </select>
        <select v-model="localSortOrder" class="select compact" @change="emit('sort-order-change', localSortOrder)">
          <option value="desc">Сначала новые</option>
          <option value="asc">Сначала старые</option>
        </select>
        <select v-model.number="localPageSize" class="select compact" @change="emit('page-size-change', localPageSize)">
          <option :value="5">5 на странице</option>
          <option :value="10">10 на странице</option>
          <option :value="20">20 на странице</option>
          <option :value="50">50 на странице</option>
        </select>
      </div>
    </div>

    <div v-if="meta" class="meta-row">
      <span>Страница {{ meta.page }} из {{ meta.total_pages }}</span>
      <span>Найдено {{ meta.total_items }}</span>
    </div>

    <div v-if="tasks.length" class="task-grid">
      <article v-for="task in tasks" :key="task.id" class="task-item">
        <div class="task-topline">
          <span class="status-pill" :class="task.status">{{ task.status === "done" ? "Готово" : "В работе" }}</span>
          <small>{{ formatDate(task.updated_at) }}</small>
        </div>

        <div v-if="editingTaskId === task.id" class="grid">
          <input v-model="editForm.title" class="input" type="text" />
          <textarea v-model="editForm.description" class="textarea" />
          <div class="inline-actions">
            <button class="btn" type="button" @click="saveTask(task.id)">Сохранить</button>
            <button class="btn ghost" type="button" @click="cancelEditing">Отмена</button>
          </div>
        </div>

        <div v-else>
          <h3>{{ task.title }}</h3>
          <p>{{ task.description || "Без описания" }}</p>
          <div class="inline-actions">
            <button class="btn secondary" type="button" @click="emit('toggle', task.id)">
              {{ task.status === "done" ? "Вернуть в работу" : "Отметить готовой" }}
            </button>
            <button class="btn ghost" type="button" @click="startEditing(task)">Редактировать</button>
            <button v-if="task.is_deleted" class="btn" type="button" @click="emit('restore', task.id)">Восстановить</button>
            <button v-else class="btn danger" type="button" @click="emit('archive', task.id)">В архив</button>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="empty-state">
      <strong>{{ emptyTitle }}</strong>
      <p>{{ emptyText }}</p>
    </div>

    <div v-if="meta" class="pagination-row">
      <button class="btn ghost" type="button" :disabled="!meta.has_previous" @click="emit('page-change', meta.page - 1)">
        Назад
      </button>
      <button class="btn ghost" type="button" :disabled="!meta.has_next" @click="emit('page-change', meta.page + 1)">
        Вперёд
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";

import type { PaginationMeta, Task, TaskSummary } from "@/types";

const props = defineProps<{
  tasks: Task[];
  title: string;
  headingEyebrow: string;
  search: string;
  statusFilter: string;
  sortBy: string;
  sortOrder: string;
  pageSize: number;
  meta: PaginationMeta | null;
  summary?: TaskSummary | null;
  emptyTitle?: string;
  emptyText?: string;
}>();

const emit = defineEmits<{
  archive: [taskId: string];
  restore: [taskId: string];
  toggle: [taskId: string];
  update: [taskId: string, payload: { title: string; description: string }];
  "search-change": [value: string];
  "status-change": [value: string];
  "sort-by-change": [value: string];
  "sort-order-change": [value: string];
  "page-change": [page: number];
  "page-size-change": [pageSize: number];
}>();

const editingTaskId = ref<string | null>(null);
const editForm = reactive({
  title: "",
  description: "",
});
const localSearch = ref(props.search);
const localStatus = ref(props.statusFilter);
const localSortBy = ref(props.sortBy);
const localSortOrder = ref(props.sortOrder);
const localPageSize = ref(props.pageSize);

watch(
  () => props.search,
  (value) => {
    localSearch.value = value;
  },
);

watch(
  () => props.statusFilter,
  (value) => {
    localStatus.value = value;
  },
);

watch(
  () => props.sortBy,
  (value) => {
    localSortBy.value = value;
  },
);

watch(
  () => props.sortOrder,
  (value) => {
    localSortOrder.value = value;
  },
);

watch(
  () => props.pageSize,
  (value) => {
    localPageSize.value = value;
  },
);

function startEditing(task: Task) {
  editingTaskId.value = task.id;
  editForm.title = task.title;
  editForm.description = task.description;
}

function cancelEditing() {
  editingTaskId.value = null;
}

function saveTask(taskId: string) {
  emit("update", taskId, { ...editForm });
  editingTaskId.value = null;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<style scoped>
.section-head,
.filters,
.task-topline,
.meta-row,
.pagination-row {
  display: flex;
  gap: 12px;
}

.section-head {
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  font-size: 1.35rem;
}

.summary-line {
  margin: 10px 0 0;
  color: #5f6c7c;
}

.filters {
  flex-wrap: wrap;
}

.compact {
  min-width: 180px;
}

.meta-row,
.pagination-row {
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.meta-row {
  color: #667587;
  margin-bottom: 16px;
}

.pagination-row {
  margin-top: 18px;
}

.task-grid {
  display: grid;
  gap: 14px;
}

.task-item {
  border-radius: 22px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(18, 35, 56, 0.08);
}

.task-topline {
  justify-content: space-between;
  color: #667587;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.task-item h3 {
  margin: 0 0 10px;
  font-size: 1.18rem;
}

.task-item p {
  margin: 0 0 16px;
  color: #566477;
}

.status-pill {
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.status-pill.todo {
  background: rgba(45, 94, 195, 0.12);
  color: #264f9f;
}

.status-pill.done {
  background: rgba(19, 137, 89, 0.12);
  color: #166442;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.72rem;
  color: #738194;
  margin-bottom: 8px;
}

.empty-state {
  border-radius: 22px;
  padding: 24px;
  background: rgba(19, 34, 56, 0.04);
}

.empty-state p {
  margin: 10px 0 0;
  color: #5e6d7f;
}

@media (max-width: 960px) {
  .section-head {
    flex-direction: column;
  }

  .filters {
    width: 100%;
  }

  .compact {
    min-width: 0;
    flex: 1 1 180px;
  }
}
</style>
