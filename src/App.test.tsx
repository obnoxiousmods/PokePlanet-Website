import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "./App";

vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("offline"))));

describe("PokePlanet website", () => {
  it("renders the core value proposition", async () => {
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
    expect(screen.getByRole("heading", { name: /permanent/i })).toBeInTheDocument();
    expect(screen.getAllByText(/no pay-to-win/i)).not.toHaveLength(0);
    await waitFor(() => expect(screen.getByText(/server status unavailable/i)).toBeInTheDocument());
  });

  it("renders platform download choices", () => {
    render(<MemoryRouter initialEntries={["/download"]}><App /></MemoryRouter>);
    expect(screen.getByRole("tab", { name: /windows/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /android/i })).toBeInTheDocument();
  });
});
