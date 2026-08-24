import React from "react";
import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";

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
  const userContext = useUser();
  const petitioner = usePetitioner();
  const petitions = usePetitions();
  const navBlock = useNavBlock();

  return (
    <div>
      <div data-testid="auth-context">
        {auth !== undefined ? "auth-loaded" : "no-auth"}
      </div>
      <div data-testid="user-context">
        {userContext !== undefined ? "user-loaded" : "no-user"}
      </div>
      <div data-testid="user-data">
        {userContext ? JSON.stringify(userContext) : ""}
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
  it("renders all expected context providers correctly and forwards seeded user data", async () => {
    const customUser = {
      user: {
        username: "testuser",
        email: "test@example.com",
        first_name: "Test",
        last_name: "User",
      },
      organization: {
        name: "Test Org",
        address: {},
        phone: "",
        pk: 1,
        url: "",
      },
      attorney: {
        bar: "",
        name: "",
        pk: 1,
        url: "",
        user_id: 1,
      },
    };

    renderWithProviders(<TestComponent />, { user: customUser });

    expect(screen.getByTestId("auth-context")).toHaveTextContent("auth-loaded");
    expect(screen.getByTestId("user-context")).toHaveTextContent("user-loaded");
    expect(screen.getByTestId("petitioner-context")).toHaveTextContent("petitioner-loaded");
    expect(screen.getByTestId("petitions-context")).toHaveTextContent("petitions-loaded");
    expect(screen.getByTestId("navblock-context")).toHaveTextContent("navblock-loaded");

    // Wait for the async api.getUserProfile promise to resolve and populate state
    await waitFor(() => {
      expect(screen.getByTestId("user-data")).toHaveTextContent("testuser");
    });
  });

  it("initializes with a custom route and exposes the history object", () => {
    const customRoute = "/custom-test-route";
    const { history } = renderWithProviders(<TestComponent />, {
      route: customRoute,
    });

    expect(history.location.pathname).toBe(customRoute);
  });
});
