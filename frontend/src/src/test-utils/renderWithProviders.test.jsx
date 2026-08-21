import React from "react";
import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";

import { renderWithProviders } from "./renderWithProviders";
import { useAuth } from "../context/auth";
import { useUser } from "../context/user";
import { usePetitioner } from "../context/petitioner";
import { usePetitions } from "../context/petitions";
import { useNavBlock } from "../context/navBlockContext";

vi.mock("../services/api", () => ({
  default: {
    getUserProfile: vi.fn(),
  },
}));

function TestComponent() {
  const auth = useAuth();
  const user = useUser();
  const petitioner = usePetitioner();
  const petitions = usePetitions();
  const navBlock = useNavBlock();

  return (
    <div>
      <div data-testid="auth-context">
        {auth !== undefined ? "auth-loaded" : "no-auth"}
      </div>
      <div data-testid="user-context">
        {user !== undefined ? "user-loaded" : "no-user"}
      </div>
      <div data-testid="petitioner-context">
        {petitioner !== undefined ? "petitioner-loaded" : "no-petitioner"}
      </div>
      <div data-testid="petitions-context">
        {petitions !== undefined ? "petitions-loaded" : "no-petitions"}
      </div>
      <div data-testid="navblock-context">
        {navBlock !== undefined ? "navblock-loaded" : "no-navblock"}
      </div>
    </div>
  );
}

describe("renderWithProviders", () => {
  it("renders all expected context providers correctly", () => {
    renderWithProviders(<TestComponent />);

    expect(screen.getByTestId("auth-context")).toHaveTextContent("auth-loaded");
    expect(screen.getByTestId("user-context")).toHaveTextContent("user-loaded");
    expect(screen.getByTestId("petitioner-context")).toHaveTextContent("petitioner-loaded");
    expect(screen.getByTestId("petitions-context")).toHaveTextContent("petitions-loaded");
    expect(screen.getByTestId("navblock-context")).toHaveTextContent("navblock-loaded");
  });

  it("initializes with a custom route and exposes the location", () => {
    const customRoute = "/custom-test-route";
    const { location } = renderWithProviders(<TestComponent />, {
      route: customRoute,
    });

    expect(location.pathname).toBe(customRoute);
  });
});
