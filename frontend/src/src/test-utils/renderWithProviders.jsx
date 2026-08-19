import React from "react";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import api from "../services/api";
import { AuthProvider } from "../context/auth";
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
    } = {}
) {
    localStorage.setItem(
        "tokens",
        JSON.stringify({
            access: "test-access-token",
        })
    );

    api.getUserProfile.mockResolvedValue(user);

    return render(
        <MemoryRouter initialEntries={[route]}>
            <AuthProvider>
                <PetitionerProvider>
                    <PetitionsProvider>
                        <UserProvider>
                            <NavBlockProvider>
                                {ui}
                            </NavBlockProvider>
                        </UserProvider>
                    </PetitionsProvider>
                </PetitionerProvider>
            </AuthProvider>
        </MemoryRouter>
    );
}
