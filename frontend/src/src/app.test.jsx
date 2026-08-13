import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import App from "./App";
import api from "./services/api";

//otherwise vitest will not use the mock and will instead use the real API service
vi.mock("./services/api");

describe("App", () => {
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

        // Login
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

        // The authenticated application loads the attorney list.
        const attorneySelect = await screen.findByRole("combobox", {
            name: "",
        });

        expect(
            screen.getByText("Test Attorney")
        ).toBeInTheDocument();

        // Select the attorney and continue.
        await user.selectOptions(attorneySelect, "1");
        await user.click(
            screen.getByRole("button", { name: "Select" })
        );

        // Verify the API seam was actually used.
        expect(api.login).toHaveBeenCalledWith("testuser", "password");
        expect(api.getAttorneys).toHaveBeenCalledTimes(1);
        expect(api.updateProfile).toHaveBeenCalledWith({
            attorney: 1,
            organization: 1,
            user_id: 123,
        });

        // The real App navigated to the upload route.
        expect(window.location.pathname).toBe("/upload");
    });
});
