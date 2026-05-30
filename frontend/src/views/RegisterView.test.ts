import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import RegisterView from "@/views/RegisterView.vue";

const push = vi.fn();
const register = vi.fn().mockResolvedValue(undefined);

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
    register,
  }),
}));

describe("RegisterView", () => {
  it("submits registration payload with selected role", async () => {
    const wrapper = mount(RegisterView);

    await wrapper.get("#username").setValue("vip-user");
    await wrapper.get("#email").setValue("vip@example.com");
    await wrapper.get("#password").setValue("strong-password");
    await wrapper.get("#role").setValue("vip");
    await wrapper.get("form").trigger("submit.prevent");

    expect(register).toHaveBeenCalledWith({
      username: "vip-user",
      email: "vip@example.com",
      password: "strong-password",
      role: "vip",
    });
    expect(push).toHaveBeenCalledWith({ name: "dashboard" });
  });
});
