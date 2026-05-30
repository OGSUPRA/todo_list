import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import TaskList from "@/components/TaskList.vue";

describe("TaskList", () => {
  it("emits actions for task controls", async () => {
    const wrapper = mount(TaskList, {
      props: {
        tasks: [
          {
            id: "1",
            title: "Перенести проект",
            description: "На новый стек",
            status: "todo",
            is_deleted: false,
            created_at: "2026-05-30T12:00:00Z",
            updated_at: "2026-05-30T12:00:00Z",
          },
        ],
        title: "Список",
        headingEyebrow: "Тест",
        search: "",
        statusFilter: "",
        sortBy: "created_at",
        sortOrder: "desc",
        pageSize: 10,
        meta: {
          page: 1,
          page_size: 10,
          total_items: 1,
          total_pages: 1,
          has_next: false,
          has_previous: false,
          sort_by: "created_at",
          sort_order: "desc",
        },
        summary: {
          total: 1,
          todo: 1,
          done: 0,
          archived: 0,
        },
      },
    });

    const buttons = wrapper.findAll("button");
    await buttons[0].trigger("click");
    await buttons[1].trigger("click");
    await buttons[2].trigger("click");

    expect(wrapper.emitted("toggle")).toBeTruthy();
    expect(wrapper.emitted("archive")).toBeTruthy();
  });

  it("emits filter and paging events", async () => {
    const wrapper = mount(TaskList, {
      props: {
        tasks: [],
        title: "Список",
        headingEyebrow: "Тест",
        search: "",
        statusFilter: "",
        sortBy: "created_at",
        sortOrder: "desc",
        pageSize: 10,
        meta: {
          page: 2,
          page_size: 10,
          total_items: 25,
          total_pages: 3,
          has_next: true,
          has_previous: true,
          sort_by: "created_at",
          sort_order: "desc",
        },
        summary: {
          total: 25,
          todo: 20,
          done: 4,
          archived: 1,
        },
      },
    });

    await wrapper.get('input[type="search"]').setValue("api");
    await wrapper.findAll("select")[0].setValue("done");
    await wrapper.findAll("select")[1].setValue("title");
    await wrapper.findAll("select")[2].setValue("asc");
    await wrapper.findAll("select")[3].setValue("20");
    await wrapper.findAll("button")[1].trigger("click");

    expect(wrapper.emitted("search-change")).toBeTruthy();
    expect(wrapper.emitted("status-change")).toBeTruthy();
    expect(wrapper.emitted("sort-by-change")).toBeTruthy();
    expect(wrapper.emitted("sort-order-change")).toBeTruthy();
    expect(wrapper.emitted("page-size-change")).toBeTruthy();
    expect(wrapper.emitted("page-change")).toBeTruthy();
  });
});
