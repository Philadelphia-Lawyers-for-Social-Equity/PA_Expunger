import { render, screen } from "@testing-library/react";
import { useEffect, useState } from "react";
import { describe, expect, it, vi } from "vitest";


vi.mock("./services/api");
/*
 * This import now receives the mocked version of services/api.js above,
 * rather than the real Axios-backed implementation.
 *
 * Individual tests can configure the mocked methods with helpers such as
 * mockResolvedValue() and mockRejectedValue().
 */
import api from "./services/api";

/*
 * Small component used only to demonstrate the testing pattern.
 *
 * It consumes the same api service that a real application component would,
 * allowing the test below to demonstrate both React rendering and API
 * mocking without adding test-only code to the production application.
 */
function UserGreeting() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        api.getUserProfile().then(setUser);
    }, []);

    if (!user) {
        return <div>Loading...</div>;
    }

    return <h1>Hello, {user.first_name}!</h1>;
}

describe("API mocking", () => {
    it("renders data returned by the mocked API", async () => {
        /*
         * Configure the automatically generated mock for this specific test.
         *
         * Vitest provides mocked implementations for the API methods; tests
         * decide what each API call should return.
         */
        api.getUserProfile.mockResolvedValue({
            first_name: "Test User",
        });

        /*
         * Render the component in jsdom using React Testing Library.
         *
         * No real backend request occurs because services/api.js was mocked
         * above.
         */
        render(<UserGreeting />);

        /*
         * findByRole waits for the asynchronous API result to update the
         * component before checking the rendered DOM.
         */
        expect(
            await screen.findByRole("heading", {
                name: "Hello, Test User!",
            })
        ).toBeInTheDocument();

        /*
         * Also verify that the component actually used the API seam.
         * This helps catch tests that accidentally pass without making the
         * expected API call.
         */
        expect(api.getUserProfile).toHaveBeenCalledTimes(1);
    });
});
