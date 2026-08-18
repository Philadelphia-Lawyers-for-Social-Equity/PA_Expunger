import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

function Hello() {
    return <h1>Hello, PA Expunger!</h1>;
}

describe("React testing setup", () => {
    it("renders a React component", () => {
        render(<Hello />);

        expect(
            screen.getByRole("heading", { name: "Hello, PA Expunger!" })
        ).toBeInTheDocument();
    });
});
