import axios from "axios";
import { TOKEN_STORAGE_KEY } from "../context/auth";

// Deliberately same-origin: Django serves the SPA and the API from one host in
// production, so there is no separate backend URL to configure there. VITE_BACKEND_HOST
// covers the dev case, where the Vite server and Django run on different ports.
const BASE_URL = import.meta.env.VITE_BACKEND_HOST || window.location.origin;

const apiClient = axios.create({
    baseURL: BASE_URL,
});

// Automatically attaches JWT access token to outgoing requests
apiClient.interceptors.request.use(
    (config) => {
        const storedTokens = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (storedTokens) {
            try {
                const parsedTokens = JSON.parse(storedTokens);
                const accessToken = parsedTokens?.access;
                if (accessToken) {
                    config.headers["Authorization"] = `Bearer ${accessToken}`;
                }
            } catch (e) {
                console.error("Could not parse tokens from localStorage or attach auth header:", e);
            }
        }
        return config;
    },
    (error) => {
        console.error(`Request rejected: ${error}`);
        return Promise.reject(error);
    }
);

// Decodes error bodies that came back as binary.
//
// `responseType: "arraybuffer"` is set on the two .docx endpoints so a success
// can be turned into a Blob, but axios applies it to the error response too.
// The backend's `{"detail": "..."}` therefore arrives as an ArrayBuffer, and no
// caller can read `.detail` off it -- which is why every message those two
// endpoints produce has been invisible.
//
// Doing it here rather than in the two methods means `error.response.data` has
// the same shape on every endpoint, so a caller never has to know which kind of
// response it asked for.
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        const data = error.response?.data;
        if (data instanceof ArrayBuffer) {
            const text = new TextDecoder().decode(data);
            try {
                error.response.data = JSON.parse(text);
            } catch {
                // Not JSON -- an HTML error page, say. Keep it as text rather
                // than dropping it; callers that check for a string body can
                // still act on it.
                error.response.data = text;
            }
        }
        return Promise.reject(error);
    }
);

const api = {
    login: async (username, password) => {
        const res = await apiClient.post(`${BASE_URL}/api/v0.2.0/auth/token/`, {username, password});
        return res.data;
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
