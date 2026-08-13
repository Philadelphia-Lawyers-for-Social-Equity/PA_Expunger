import { vi } from "vitest";
/**
 * Shared mock for services/api.js.
 *
 * Keep this in sync with the API service. When adding a new API method,
 * add a corresponding vi.fn() here so tests can configure its return value.
 *
 * Individual tests should use mockResolvedValue/mockRejectedValue to define
 * the response needed for that test rather than putting default responses here.
 */
export function createApiMock() {
    return {
        login: vi.fn(),
        parseDocket: vi.fn(),
        generatePetitionBlob: vi.fn(),
        generatePetitionSummaryBlob: vi.fn(),
        getAttorneys: vi.fn(),
        getAttorney: vi.fn(),
        updateProfile: vi.fn(),
        getUserProfile: vi.fn(),
    };
}

export default createApiMock();
