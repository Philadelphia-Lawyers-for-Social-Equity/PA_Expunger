import axios from "axios";
import { clearTokens, getTokens, setTokens, SESSION_ENDED } from "./tokenStore";

const BASE_URL = import.meta.env.VITE_BACKEND_HOST || "http://localhost:8000";

const apiClient = axios.create({
    baseURL: BASE_URL,
});

// Login and refresh use their own client: they send no access token, and a 401 from
// either means the credentials themselves were rejected, so running them through the
// interceptors below would only start a refresh loop.
const authClient = axios.create({
    baseURL: BASE_URL,
});

// Automatically attaches JWT access token to outgoing requests
apiClient.interceptors.request.use(
    (config) => {
        const accessToken = getTokens()?.access;
        if (accessToken) {
            config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => {
        console.error(`Request rejected: ${error}`);
        return Promise.reject(error);
    }
);

// One refresh at a time. Not an optimization: the backend rotates refresh tokens and
// blacklists the one it just consumed, so a second concurrent refresh would present an
// already-blacklisted token, get a 401, and end the session. A request that 401s while a
// refresh is in flight waits on this same promise instead of starting its own.
let refreshRequest = null;

async function requestNewTokens() {
    const tokens = getTokens();
    if (!tokens?.refresh) {
        // An access token on its own cannot be renewed, so there is nothing to recover.
        clearTokens(SESSION_ENDED.CREDENTIALS_REJECTED);
        throw new Error("No refresh token is stored.");
    }
    try {
        const res = await authClient.post(`${BASE_URL}/api/v0.2.0/auth/refresh/`, {refresh: tokens.refresh});
        // The response carries a new access token, and a new refresh token too if the backend
        // is configured to rotate them.
        const refreshedTokens = {...tokens, ...res.data};
        setTokens(refreshedTokens);
        return refreshedTokens;
    } catch (error) {
        // Nothing but the refresh token authenticates this endpoint, so a response at all
        // means it was refused — expired, malformed, or blacklisted by a rotation
        // elsewhere — and none of that is recoverable. Dropping the pair is as far as this
        // layer decides; what the user is told about it is the auth context's call. No
        // response is a network failure instead, which the caller retries.
        if (error.response) {
            clearTokens(SESSION_ENDED.CREDENTIALS_REJECTED);
        }
        throw error;
    }
}

// Retries a request once against a freshly refreshed access token. If the refresh itself
// fails the original 401 surfaces, by which point the pair has already been cleared.
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const request = error.config;
        if (error.response?.status !== 401 || !request || request.retriedAfterRefresh) {
            return Promise.reject(error);
        }
        request.retriedAfterRefresh = true;

        try {
            await api.refreshTokens();
        } catch (refreshError) {
            console.error("Could not refresh the access token:", refreshError);
            return Promise.reject(error);
        }
        return apiClient(request);
    }
);

const api = {
    login: async (username, password) => {
        const res = await authClient.post(`${BASE_URL}/api/v0.2.0/auth/token/`, {username, password});
        return res.data;
    },

    // Exchanges the stored refresh token for a new access token and stores the result.
    // Not async: concurrent callers must all receive the same promise. See refreshRequest comment.
    refreshTokens: () => {
        if (!refreshRequest) {
            refreshRequest = requestNewTokens().finally(() => {
                refreshRequest = null;
            });
        }
        return refreshRequest;
    },

    parseDocket: async (formData) => {
        const res = await apiClient.post(`${BASE_URL}/api/v0.2.0/petition/parse-docket/`, formData);
        return res.data;
    },

    generatePetitionBlob: async (petitionFields) => {
        const res = await apiClient.post(
            `${BASE_URL}/api/v0.2.0/petition/generate/`,
            petitionFields,
            {responseType: "arraybuffer"}
        );
        return new Blob([res.data],
            {type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})
    },

    generatePetitionSummaryBlob: async (summary) => {
        const res = await apiClient.post(
            `${BASE_URL}/api/v0.2.0/petition/generator-report/`,
            summary,
            {responseType: "arraybuffer"}
        );
        return new Blob([res.data],
            {type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})
    },

    getAttorneys: async () => {
        const res = await apiClient.get(`${BASE_URL}/api/v0.2.0/expunger/attorneys/`);
        return res.data;
    },

    getAttorney: async (attorney_pk) => {
        const res = await apiClient.get(`${BASE_URL}/api/v0.2.0/expunger/attorney/${attorney_pk}`);
        return res.data;
    },

    updateProfile: async (profileData) => {
        const res = await apiClient.put(
            `${BASE_URL}/api/v0.2.0/expunger/my-profile/`,
            profileData
        );
        return res;
    },

    getUserProfile: async () => {
        const res = await apiClient.get(`${BASE_URL}/api/v0.2.0/expunger/my-profile/`);
        return res.data;
    },
};

export default api;
