import React from "react";
import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../services/api");

import { useUser } from "../context/user";
import { renderWithProviders } from "./renderWithProviders";

function TestComponent() {
    const { user } = useUser();

    return <div>{user.user.first_name}</div>;
}

describe("renderWithProviders", () => {
    it("renders with the application providers and authenticated user", async () => {
        renderWithProviders(<TestComponent />, {
            user: {
                user: {
                    email: "test@example.com",
                    first_name: "Test",
                    last_name: "User",
                    username: "testuser",
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
        });

        expect(
            await screen.findByText("Test")
        ).toBeInTheDocument();
    });
});
