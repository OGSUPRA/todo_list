import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import LoginView from "@/views/LoginView.vue";

const push = vi.fn();
const login = vi.fn().mockResolvedValue(undefined);

vi.mock("vue-router", () => ({
  RouterLink: {
    template: "<a><slot /></a>",
  },
  useRouter: () => ({
    push,
  }),
}));

vi.mock("@/stores/auth", () => ({
  useAuthStore: () => ({
    login,
  }),
}));

describe("LoginView", () => {
  it("submits credentials and redirects to dashboard", async () => {
    const wrapper = mount(LoginView);

    await wrapper.get("#login").setValue("demo");
    await wrapper.get("#password").setValue("strong-password");
    await wrapper.get("form").trigger("submit.prevent");

    expect(login).toHaveBeenCalledWith({
      username: "demo",
      password: "strong-password",
    });
    expect(push).toHaveBeenCalledWith({ name: "dashboard" });
  });
});
