import React from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, useHistory } from "react-router-dom";
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
      "renderWithProviders requires api.getUserProfile to be a mock function. " +
        'Mock the api module in this test file, e.g. vi.mock("<relative path>/services/api").',
    );
  }

  api.getUserProfile.mockResolvedValue(user);

  let history;

  function HistoryProbe() {
    history = useHistory();
    return null;
  }

  const result = render(
    <MemoryRouter initialEntries={[route]}>
      <HistoryProbe />
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
    history,
  };
}
