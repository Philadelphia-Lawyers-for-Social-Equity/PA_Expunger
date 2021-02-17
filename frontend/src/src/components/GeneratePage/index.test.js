import React from "react";
import ReactDOM from "react-dom";
import GeneratePage from "./GeneratePage";

it("renders without crashing", () => {
    const div = document.createElement("div");
    ReactDOM.render(<GeneratePage />, div);
});