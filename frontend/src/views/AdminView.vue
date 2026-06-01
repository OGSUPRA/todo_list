<template>
  <AppShell
    title="Админ-панель и аудит"
    subtitle="Следите за ролями, запросами и поведением системы из одного экрана, не заходя в контейнеры вручную."
  >
    <div v-if="notice" class="notice success fade-up">{{ notice }}</div>
    <div v-if="error" class="notice error fade-up">{{ error }}</div>

    <section class="surface card fade-up">
      <div class="section-head">
        <div>
          <div class="eyebrow">Операции</div>
          <h2>Логи и база</h2>
          <p class="section-copy">Открывайте просмотр логов и PostgreSQL прямо из админки, не вспоминая отдельные URL и порты.</p>
        </div>
      </div>
      <div class="link-grid">
        <a
          v-for="item in monitoringEntries"
          :key="item.label"
          class="monitor-link"
          :class="`monitor-link--${item.tone}`"
          :href="item.url"
          target="_blank"
          rel="noreferrer"
        >
          <div class="monitor-topline">
            <span class="monitor-badge">{{ item.badge }}</span>
            <span class="monitor-path">{{ item.path }}</span>
          </div>
          <div class="monitor-body">
            <strong>{{ item.label }}</strong>
            <p>{{ item.description }}</p>
          </div>
          <div class="monitor-footer">
            <span class="monitor-url">{{ item.url }}</span>
            <span class="monitor-action">{{ item.action }}</span>
          </div>
        </a>
      </div>
    </section>

    <div class="stats-grid">
      <section class="surface card fade-up stat-panel stat-panel--roles">
        <div class="panel-head">
          <div>
            <div class="eyebrow">Роли</div>
            <h2>Распределение доступа</h2>
            <p class="panel-copy">{{ rolesInsight }}</p>
          </div>
        </div>
        <div class="spotlight-row">
          <div class="spotlight-card">
            <span class="spotlight-label">Ведущая роль</span>
            <strong>{{ roleLead.label }}</strong>
            <span class="spotlight-value">{{ roleLead.value }}</span>
          </div>
        </div>
        <div class="chip-grid">
          <div v-for="metric in overview?.role_counts ?? []" :key="metric.label" class="metric-chip">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>
      </section>

      <section class="surface card fade-up stat-panel stat-panel--tasks">
        <div class="panel-head">
          <div>
            <div class="eyebrow">Задачи</div>
            <h2>Сводка по продукту</h2>
            <p class="panel-copy">{{ tasksInsight }}</p>
          </div>
        </div>
        <div class="spotlight-row">
          <div class="spotlight-card">
            <span class="spotlight-label">Всего задач</span>
            <strong>{{ taskLead.label }}</strong>
            <span class="spotlight-value">{{ taskLead.value }}</span>
          </div>
        </div>
        <div class="chip-grid">
          <div v-for="metric in overview?.task_counts ?? []" :key="metric.label" class="metric-chip">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="analytics-grid">
      <section class="surface card fade-up analytics-panel analytics-panel--traffic">
        <div class="panel-head">
          <div>
            <div class="eyebrow">Трафик</div>
            <h2>Запросы по дням</h2>
            <p class="panel-copy">{{ trafficInsight }}</p>
          </div>
          <div class="panel-kicker">{{ totalRequests }} запросов</div>
        </div>
        <div class="bar-list">
          <div v-for="metric in overview?.request_volume ?? []" :key="metric.label" class="bar-item">
            <div class="bar-head">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.value }}</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill primary" :style="{ width: toBarWidth(metric.value, requestMax) }"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="surface card fade-up analytics-panel analytics-panel--actions">
        <div class="panel-head">
          <div>
            <div class="eyebrow">Действия</div>
            <h2>Наиболее частые события</h2>
            <p class="panel-copy">{{ actionsInsight }}</p>
          </div>
          <div class="panel-kicker">{{ actionLead.value }} пиков</div>
        </div>
        <div class="bar-list">
          <div v-for="metric in overview?.action_breakdown ?? []" :key="metric.label" class="bar-item">
            <div class="bar-head">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.value }}</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill accent" :style="{ width: toBarWidth(metric.value, actionMax) }"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="surface card fade-up analytics-panel analytics-panel--status">
        <div class="panel-head">
          <div>
            <div class="eyebrow">Статусы</div>
            <h2>Распределение ответов</h2>
            <p class="panel-copy">{{ statusInsight }}</p>
          </div>
        </div>
        <div class="metric-list elevated-list">
          <div v-for="metric in overview?.status_breakdown ?? []" :key="metric.label" class="metric-item">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>
      </section>

      <section class="surface card fade-up analytics-panel analytics-panel--paths">
        <div class="panel-head">
          <div>
            <div class="eyebrow">Маршруты</div>
            <h2>Самые горячие endpoint'ы</h2>
            <p class="panel-copy">{{ pathsInsight }}</p>
          </div>
        </div>
        <div class="metric-list elevated-list">
          <div v-for="metric in overview?.top_paths ?? []" :key="metric.label" class="metric-item">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>
      </section>
    </div>

    <section class="surface card fade-up">
      <div class="section-head">
        <div>
          <div class="eyebrow">Пользователи</div>
          <h2>Роли и нагрузка</h2>
        </div>
        <div class="filters">
          <button class="btn ghost" type="button" :disabled="!usersMeta?.has_previous" @click="changeUsersPage(usersMeta!.page - 1)">
            Назад
          </button>
          <button class="btn ghost" type="button" :disabled="!usersMeta?.has_next" @click="changeUsersPage(usersMeta!.page + 1)">
            Вперёд
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Пользователь</th>
              <th>Роль</th>
              <th>Задачи</th>
              <th>Архив</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in adminUsers" :key="user.id">
              <td>
                <strong>{{ user.username }}</strong>
                <div class="muted-line">{{ user.email }}</div>
              </td>
              <td>
                <select v-model="roleDrafts[user.id]" class="select compact-cell">
                  <option value="admin">Admin</option>
                  <option value="vip">VIP</option>
                  <option value="standard">Standart</option>
                </select>
              </td>
              <td>{{ user.task_summary.total }} / {{ user.task_summary.done }} done</td>
              <td>{{ user.task_summary.archived }}</td>
              <td>
                <button class="btn ghost" type="button" @click="saveRole(user.id)">Сохранить роль</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="surface card fade-up">
      <div class="section-head">
        <div>
          <div class="eyebrow">Аудит</div>
          <h2>Журнал действий</h2>
        </div>
        <div class="filters">
          <input v-model="auditFilters.category" class="input compact" type="text" placeholder="Фильтр по category" @change="reloadAudit" />
          <input v-model="auditFilters.action" class="input compact" type="text" placeholder="Фильтр по action" @change="reloadAudit" />
        </div>
      </div>

      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Когда</th>
              <th>Событие</th>
              <th>Пользователь</th>
              <th>HTTP</th>
              <th>Контекст</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in auditEvents" :key="event.id">
              <td>{{ formatDate(event.created_at) }}</td>
              <td>
                <strong>{{ event.action }}</strong>
                <div class="muted-line">{{ event.category }}</div>
              </td>
              <td>
                <span>{{ event.username || "system" }}</span>
                <div class="muted-line">{{ event.role || "n/a" }}</div>
              </td>
              <td>
                <span>{{ event.method }} {{ event.status_code }}</span>
                <div class="muted-line">{{ event.duration_ms }} ms</div>
              </td>
              <td>
                <span>{{ event.path }}</span>
                <div class="muted-line">{{ event.client_ip || "без IP" }}</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-row">
        <button class="btn ghost" type="button" :disabled="!auditMeta?.has_previous" @click="changeAuditPage(auditMeta!.page - 1)">
          Назад
        </button>
        <span v-if="auditMeta">Страница {{ auditMeta.page }} из {{ auditMeta.total_pages }}</span>
        <button class="btn ghost" type="button" :disabled="!auditMeta?.has_next" @click="changeAuditPage(auditMeta!.page + 1)">
          Вперёд
        </button>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import AppShell from "@/components/AppShell.vue";
import { api } from "@/lib/api";
import type {
  AdminOverviewResponse,
  AdminUser,
  AdminUsersResponse,
  AuditEvent,
  AuditEventsResponse,
  NamedMetric,
  PaginationMeta,
  UserRole,
} from "@/types";

const overview = ref<AdminOverviewResponse | null>(null);
const adminUsers = ref<AdminUser[]>([]);
const usersMeta = ref<PaginationMeta | null>(null);
const auditEvents = ref<AuditEvent[]>([]);
const auditMeta = ref<PaginationMeta | null>(null);
const roleDrafts = reactive<Record<string, UserRole>>({});
const notice = ref("");
const error = ref("");

const usersPage = ref(1);
const auditPage = ref(1);
const auditFilters = reactive({
  category: "",
  action: "",
});

const monitoringEntries = computed(() =>
  overview.value
    ? [
        {
          label: "Dozzle",
          url: overview.value.monitoring.dozzle,
          badge: "Logs",
          path: "/dozzle/",
          description: "Смотрите live-логи контейнеров и быстро проверяйте, что происходит с API, web и PostgreSQL.",
          action: "Открыть Dozzle",
          tone: "logs",
        },
        {
          label: "pgweb",
          url: overview.value.monitoring.pgweb,
          badge: "SQL",
          path: "/db/",
          description: "Переход в лёгкий интерфейс PostgreSQL для таблиц, запросов и быстрой серверной диагностики.",
          action: "Открыть pgweb",
          tone: "db",
        },
      ]
    : [],
);

const requestMax = computed(() => Math.max(1, ...(overview.value?.request_volume ?? []).map((item) => item.value)));
const actionMax = computed(() => Math.max(1, ...(overview.value?.action_breakdown ?? []).map((item) => item.value)));
const roleLead = computed(() => maxMetric(overview.value?.role_counts ?? []));
const taskLead = computed(() => findMetric(overview.value?.task_counts ?? [], "total") ?? maxMetric(overview.value?.task_counts ?? []));
const actionLead = computed(() => maxMetric(overview.value?.action_breakdown ?? []));
const statusLead = computed(() => maxMetric(overview.value?.status_breakdown ?? []));
const pathLead = computed(() => maxMetric(overview.value?.top_paths ?? []));
const requestLead = computed(() => maxMetric(overview.value?.request_volume ?? []));
const totalRequests = computed(() => sumMetrics(overview.value?.request_volume ?? []));
const rolesInsight = computed(() => `${formatMetricLabel(roleLead.value.label)} сейчас самая заметная роль по числу пользователей.`);
const tasksInsight = computed(() => `${taskLead.value.value} задач отражают текущую нагрузку по продукту и архиву.`);
const trafficInsight = computed(() => `${formatMetricLabel(requestLead.value.label)} был самым активным днём по трафику.`);
const actionsInsight = computed(() => `Событие ${formatMetricLabel(actionLead.value.label)} встречается чаще остальных в аудите.`);
const statusInsight = computed(() => `Код ${formatMetricLabel(statusLead.value.label)} лидирует в распределении HTTP-ответов.`);
const pathsInsight = computed(() => `${formatMetricLabel(pathLead.value.label)} сейчас самый горячий маршрут API.`);

async function fetchOverview() {
  const { data } = await api.get<AdminOverviewResponse>("/admin/overview");
  overview.value = data;
}

async function fetchUsers() {
  const { data } = await api.get<AdminUsersResponse>("/admin/users", {
    params: {
      page: usersPage.value,
      page_size: 10,
    },
  });
  adminUsers.value = data.items;
  usersMeta.value = data.meta;
  for (const user of data.items) {
    roleDrafts[user.id] = user.role;
  }
}

async function fetchAudit() {
  const { data } = await api.get<AuditEventsResponse>("/admin/audit-events", {
    params: {
      page: auditPage.value,
      page_size: 10,
      category: auditFilters.category || undefined,
      action: auditFilters.action || undefined,
    },
  });
  auditEvents.value = data.items;
  auditMeta.value = data.meta;
}

async function saveRole(userId: string) {
  error.value = "";
  notice.value = "";
  try {
    await api.patch(`/users/${userId}/role`, { role: roleDrafts[userId] });
    notice.value = "Роль пользователя обновлена";
    await Promise.all([fetchUsers(), fetchOverview(), fetchAudit()]);
  } catch {
    error.value = "Не удалось обновить роль пользователя";
  }
}

function changeUsersPage(page: number) {
  usersPage.value = page;
  void fetchUsers();
}

function changeAuditPage(page: number) {
  auditPage.value = page;
  void fetchAudit();
}

function reloadAudit() {
  auditPage.value = 1;
  void fetchAudit();
}

function toBarWidth(value: number, max: number) {
  return `${Math.max(10, (value / max) * 100)}%`;
}

function maxMetric(items: NamedMetric[]) {
  return items.reduce<NamedMetric>(
    (best, item) => (item.value > best.value ? item : best),
    items[0] ?? { label: "нет данных", value: 0 },
  );
}

function findMetric(items: NamedMetric[], label: string) {
  return items.find((item) => item.label === label);
}

function sumMetrics(items: NamedMetric[]) {
  return items.reduce((sum, item) => sum + item.value, 0);
}

function formatMetricLabel(value: string) {
  return value.replace(/_/g, " ");
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(async () => {
  const sections = await Promise.allSettled([
    fetchOverview(),
    fetchUsers(),
    fetchAudit(),
  ]);

  const failedSections = sections.flatMap((result, index) => {
    if (result.status === "fulfilled") {
      return [];
    }

    return [index === 0 ? "обзор" : index === 1 ? "пользователи" : "аудит"];
  });

  if (!failedSections.length) {
    return;
  }

  if (failedSections.length === sections.length) {
    error.value = "Не удалось загрузить административные данные";
    return;
  }

  error.value = `Часть данных не загрузилась: ${failedSections.join(", ")}`;
});
</script>

<style scoped>
.section-head,
.filters,
.stats-grid,
.analytics-grid,
.pagination-row {
  display: flex;
  gap: 16px;
}

.section-head,
.pagination-row {
  justify-content: space-between;
  align-items: center;
}

.section-head {
  margin-bottom: 18px;
}

.section-head h2,
.surface h2 {
  margin: 0;
}

.section-copy {
  margin: 10px 0 0;
  max-width: 56ch;
  color: #667587;
}

.panel-copy {
  margin: 10px 0 0;
  max-width: 42ch;
  color: #617183;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.72rem;
  color: #738194;
  margin-bottom: 8px;
}

.filters {
  flex-wrap: wrap;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.link-grid,
.metric-list,
.bar-list {
  display: grid;
  gap: 12px;
}

.link-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.monitor-link {
  display: grid;
  gap: 18px;
  min-height: 208px;
  border-radius: 24px;
  padding: 20px;
  border: 1px solid rgba(18, 35, 56, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.52);
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
}

.monitor-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 30px rgba(19, 34, 56, 0.12);
}

.monitor-link--logs {
  background:
    radial-gradient(circle at top right, rgba(107, 164, 255, 0.24), transparent 34%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(236, 244, 255, 0.84));
}

.monitor-link--db {
  background:
    radial-gradient(circle at top right, rgba(236, 185, 95, 0.26), transparent 34%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(255, 245, 227, 0.84));
}

.monitor-topline,
.monitor-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.monitor-badge,
.monitor-action {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.monitor-link--logs .monitor-badge,
.monitor-link--logs .monitor-action {
  background: rgba(51, 94, 168, 0.12);
  color: #234985;
}

.monitor-link--db .monitor-badge,
.monitor-link--db .monitor-action {
  background: rgba(194, 138, 44, 0.12);
  color: #8b5f12;
}

.monitor-path {
  color: #718194;
  font-family: "SFMono-Regular", "Menlo", monospace;
  font-size: 0.88rem;
}

.monitor-body {
  display: grid;
  gap: 8px;
}

.monitor-body strong {
  font-size: 1.45rem;
  letter-spacing: -0.04em;
}

.monitor-body p {
  margin: 0;
  color: #57677a;
  line-height: 1.55;
}

.monitor-url,
.muted-line {
  color: #667587;
  font-size: 0.92rem;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.panel-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(19, 34, 56, 0.08);
  color: #24364f;
  font-weight: 700;
  white-space: nowrap;
}

.stat-panel,
.analytics-panel {
  position: relative;
  overflow: hidden;
}

.stat-panel::before,
.analytics-panel::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.7;
}

.stat-panel--roles::before {
  background: radial-gradient(circle at top right, rgba(88, 154, 255, 0.16), transparent 34%);
}

.stat-panel--tasks::before {
  background: radial-gradient(circle at top right, rgba(236, 185, 95, 0.18), transparent 34%);
}

.analytics-panel--traffic::before {
  background: radial-gradient(circle at top right, rgba(88, 154, 255, 0.14), transparent 32%);
}

.analytics-panel--actions::before {
  background: radial-gradient(circle at top right, rgba(236, 185, 95, 0.18), transparent 32%);
}

.analytics-panel--status::before {
  background: radial-gradient(circle at top right, rgba(84, 184, 130, 0.16), transparent 32%);
}

.analytics-panel--paths::before {
  background: radial-gradient(circle at top right, rgba(202, 126, 88, 0.16), transparent 32%);
}

.spotlight-row,
.chip-grid {
  position: relative;
  z-index: 1;
}

.spotlight-row {
  margin-bottom: 18px;
}

.spotlight-card {
  display: grid;
  gap: 8px;
  padding: 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(18, 35, 56, 0.08);
}

.spotlight-label {
  color: #718194;
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.spotlight-card strong {
  font-size: 1.7rem;
  letter-spacing: -0.05em;
}

.spotlight-value {
  font-size: 2.35rem;
  font-weight: 800;
  line-height: 1;
  color: #132238;
}

.chip-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.metric-chip {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  min-height: 60px;
  padding: 0 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(18, 35, 56, 0.08);
}

.metric-chip span {
  color: #596a7e;
}

.metric-chip strong {
  font-size: 1.1rem;
}

.metric-item,
.bar-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.metric-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(18, 35, 56, 0.08);
}

.metric-item:last-child {
  border-bottom: 0;
}

.elevated-list .metric-item {
  padding: 14px 0;
}

.bar-item {
  display: grid;
  gap: 8px;
}

.bar-track {
  height: 10px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(18, 35, 56, 0.08);
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
}

.bar-fill.primary {
  background: linear-gradient(90deg, #335ea8 0%, #6ba4ff 100%);
}

.bar-fill.accent {
  background: linear-gradient(90deg, #c28a2c 0%, #f3c56e 100%);
}

.table-wrap {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(18, 35, 56, 0.08);
  text-align: left;
  vertical-align: top;
}

.compact,
.compact-cell {
  min-width: 180px;
}

.pagination-row {
  margin-top: 18px;
  flex-wrap: wrap;
}

@media (max-width: 960px) {
  .link-grid,
  .chip-grid,
  .stats-grid,
  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters {
    width: 100%;
  }

  .panel-head {
    flex-direction: column;
  }
}
</style>
