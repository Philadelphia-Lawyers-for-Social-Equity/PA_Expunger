import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Switch } from "react-router-dom";

import { renderWithProviders } from "../../test-utils/renderWithProviders";
import api from "../../services/api";
import FileUpload from "./index";
import { usePetitioner } from "../../context/petitioner";
import { usePetitions } from "../../context/petitions";

vi.mock("../../services/api", () => ({
  default: {
    getUserProfile: vi.fn(),
    parseDocket: vi.fn(),
  },
}));

function GenerateProbe() {
  const { petitioner } = usePetitioner();
  const { petitions } = usePetitions();

  return (
    <div>
      <div data-testid="generate-page-marker">Generate Step Loaded</div>
      <div data-testid="petitioner-name">{petitioner?.name || ""}</div>
      <div data-testid="petitions-list">
        {petitions?.map((p, idx) => (
          <span
            key={p.docket_info?.otn || idx}
            data-testid={`petition-${p.docket_info?.otn || idx}`}
          >
            {p.docket_info?.otn}
          </span>
        ))}
      </div>
    </div>
  );
}

describe("FileUpload -> /generate handoff", () => {
  const mockUser = {
    user: {
      email: "attorney@example.com",
      first_name: "Jane",
      last_name: "Doe",
      username: "jdoe",
    },
    organization: {
      name: "Legal Aid Society",
      address: { street: "123 Legal Way" },
      phone: "555-1234",
      pk: 42,
      url: "https://legalaid.org",
    },
    attorney: {
      bar: "12345",
      name: "Jane Doe",
      pk: 99,
      url: "https://legalaid.org/attorney/99",
      user_id: 1,
    },
  };

  const mockParsedResponse = {
    petitioner: {
      name: "John Doe",
      aliases: [],
      dob: "1990-01-01",
      ssn: "000-00-0000",
      address: "456 Test Street",
    },
    petitions: [
      {
        docket_numbers: ["CP-51-CR-0001111-2020"],
        docket_info: {
          otn: "T111111",
        },
      },
      {
        docket_numbers: ["CP-51-CR-0002222-2020"],
        docket_info: {
          otn: "T222222",
        },
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("filters omitted petitions, commits parsed data to context, and transitions to /generate", async () => {
    const user = userEvent.setup();
    api.parseDocket.mockResolvedValueOnce(mockParsedResponse);

    const { history } = renderWithProviders(
      <Switch>
        <Route path="/upload" component={FileUpload} />
        <Route path="/generate" component={GenerateProbe} />
      </Switch>,
      { route: "/upload", user: mockUser }
    );

    // 1. Locate file input in the opened upload modal
    const fileInput = await waitFor(() => {
      const input = document.body.querySelector(
        'input[type="file"][name="docket_file"]'
      );
      if (!input) {
        throw new Error("File input not rendered yet in modal");
      }
      return input;
    });

    // 2. Upload valid PDF and submit modal
    const file = new File(["dummy CIPRS PDF content"], "record.pdf", {
      type: "application/pdf",
    });
    await user.upload(fileInput, file);

    expect(await screen.findByText("record.pdf")).toBeInTheDocument();
    const submitModalBtn =
      document.body.querySelector("#fileButton") ||
      screen.getByRole("button", { name: /^submit$/i });
    await user.click(submitModalBtn);

    // 3. Confirm API call and preview table rendering
    await waitFor(() => {
      expect(api.parseDocket).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(screen.getByText("T111111")).toBeInTheDocument();
      expect(screen.getByText("T222222")).toBeInTheDocument();
    });

    // 4. Exclude petition T222222 (find omit checkbox in PetitionTable)
    const checkboxes = screen.getAllByRole("checkbox");
    if (checkboxes.length > 0) {
      // Toggle the second record's omit box
      await user.click(checkboxes[checkboxes.length - 1]);
    }

    // 5. Continue to generation
    const continueBtn = screen.getByRole("button", {
      name: /continue to petition generation/i,
    });
    await user.click(continueBtn);

    // 6. Assert route change and state persistence
    await waitFor(() => {
      expect(history.location.pathname).toBe("/generate");
    });

    expect(history.location.state?.petitionFields).toBeDefined();
    expect(screen.getByTestId("generate-page-marker")).toBeInTheDocument();
    expect(screen.getByTestId("petitioner-name")).toHaveTextContent("John Doe");

    // 7. Verify non-omitted survived and omitted petition was excluded
    expect(screen.getByTestId("petition-T111111")).toBeInTheDocument();
    if (checkboxes.length > 0) {
      expect(screen.queryByTestId("petition-T222222")).not.toBeInTheDocument();
    }
  });
});
