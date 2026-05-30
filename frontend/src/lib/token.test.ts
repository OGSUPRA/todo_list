import { describe, expect, it } from "vitest";

import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/token";

describe("token helpers", () => {
  it("saves and clears access token in localStorage", () => {
    setAccessToken("jwt-token");
    expect(getAccessToken()).toBe("jwt-token");

    clearAccessToken();
    expect(getAccessToken()).toBeNull();
  });
});
