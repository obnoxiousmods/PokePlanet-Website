import { expect, test } from "@playwright/test";

test("home page reaches download flow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /one world/i })).toBeVisible();
  await page.getByRole("link", { name: /download alpha/i }).click();
  await expect(page).toHaveURL(/\/download$/);
  await expect(page.getByRole("tab", { name: /windows/i })).toBeVisible();
});

test("mobile navigation exposes primary links", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "mobile");
  await page.goto("/");
  await page.getByRole("button", { name: /toggle menu/i }).click();
  await expect(page.getByLabel("Primary navigation").getByRole("link", { name: "Guides" })).toBeVisible();
});
