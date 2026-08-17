import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import App from "./App";
import api from "./services/api";

vi.mock("./services/api");

describe("Login flow", () => {
    it("logs in, selects an attorney, and navigates to upload", async () => {
        api.login.mockResolvedValue({
            access: "fake-access-token",
            refresh: "fake-refresh-token",
        });

        api.getAttorneys.mockResolvedValue([
            {
                pk: 1,
                name: "Test Attorney",
                user_id: 123,
            },
        ]);

        api.updateProfile.mockResolvedValue({
            attorney: 1,
            organization: 1,
            user_id: 123,
        });

        const user = userEvent.setup();

        render(<App />);

        await user.type(
            screen.getByPlaceholderText("Username"),
            "testuser"
        );

        await user.type(
            screen.getByPlaceholderText("Password"),
            "password"
        );

        await user.click(
            screen.getByRole("button", { name: "Submit" })
        );

        const attorneySelect = await screen.findByRole("combobox");

        expect(
            screen.getByText("Test Attorney")
        ).toBeInTheDocument();

        await user.selectOptions(attorneySelect, "1");

        await user.click(
            screen.getByRole("button", { name: "Select" })
        );

        expect(api.login).toHaveBeenCalledWith("testuser", "password");
        expect(api.getAttorneys).toHaveBeenCalledTimes(1);

        expect(api.updateProfile).toHaveBeenCalledWith({
            attorney: 1,
            organization: 1,
            user_id: 123,
        });

        expect(window.location.pathname).toBe("/upload");
    });
});
