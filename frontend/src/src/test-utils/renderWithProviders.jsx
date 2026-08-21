import React from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router-dom";
import { vi } from "vitest";

import api from "../services/api";
import { AuthProvider, TOKEN_STORAGE_KEY } from "../context/auth";
import { PetitionerProvider } from "../context/petitioner";
import { PetitionsProvider } from "../context/petitions";
import { UserProvider } from "../context/user";
import { NavBlockProvider } from "../context/navBlockContext";

export function renderWithProviders(
  ui,
  {
    route = "/",
    user = {
      user: {
        email: "",
        first_name: "",
        last_name: "",
        username: "",
      },
      organization: {
        name: "",
        address: {},
        phone: "",
        pk: -1,
        url: "",
      },
      attorney: {
        bar: "",
        name: "",
        pk: -1,
        url: "",
        user_id: -1,
      },
    },
  } = {},
) {
  localStorage.setItem(
    TOKEN_STORAGE_KEY,
    JSON.stringify({
      access: "test-access-token",
    }),
  );

  if (!vi.isMockFunction(api.getUserProfile)) {
    throw new Error(
      "renderWithProviders requires the api module to be mocked. " +
        'Add vi.mock("<relative path>/services/api") to this test file.',
    );
  }

  api.getUserProfile.mockResolvedValue(user);

  let currentLocation;

  function LocationProbe() {
    currentLocation = useLocation();
    return null;
  }

  const result = render(
    <MemoryRouter initialEntries={[route]}>
      <LocationProbe />
      <AuthProvider>
        <PetitionerProvider>
          <PetitionsProvider>
            <UserProvider>
              <NavBlockProvider>{ui}</NavBlockProvider>
            </UserProvider>
          </PetitionsProvider>
        </PetitionerProvider>
      </AuthProvider>
    </MemoryRouter>,
  );

  return {
    ...result,
    get location() {
      return currentLocation;
    },
  };
}
