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
      },
    });

    const buttons = wrapper.findAll("button");
    await buttons[0].trigger("click");
    await buttons[1].trigger("click");
    await buttons[2].trigger("click");

    expect(wrapper.emitted("toggle")).toBeTruthy();
    expect(wrapper.emitted("archive")).toBeTruthy();
  });
});
