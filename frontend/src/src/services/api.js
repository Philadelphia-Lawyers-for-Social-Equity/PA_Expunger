import axios from "axios";
import { getTokens, setTokens } from "./tokenStore";

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

// One refresh at a time: every request that hits a 401 while a refresh is in flight waits
// on that same promise instead of spending another refresh of its own.
let refreshRequest = null;

async function requestNewTokens() {
    const tokens = getTokens();
    if (!tokens?.refresh) {
        throw new Error("No refresh token is stored.");
    }
    const res = await authClient.post(`${BASE_URL}/api/v0.2.0/auth/refresh/`, {refresh: tokens.refresh});
    // The response carries a new access token, and a new refresh token too if the backend
    // is configured to rotate them.
    const refreshedTokens = {...tokens, ...res.data};
    setTokens(refreshedTokens);
    return refreshedTokens;
}

function refreshTokens() {
    if (!refreshRequest) {
        refreshRequest = requestNewTokens().finally(() => {
            refreshRequest = null;
        });
    }
    return refreshRequest;
}

// Retries a request once against a freshly refreshed access token. If the refresh itself
// fails the original 401 surfaces, which is what authenticatedRequest logs out on.
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const request = error.config;
        if (error.response?.status !== 401 || !request || request.retriedAfterRefresh) {
            return Promise.reject(error);
        }
        request.retriedAfterRefresh = true;

        try {
            await refreshTokens();
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
    refreshTokens,

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
