import axios from "axios";
import {TOKEN_STORAGE_KEY,LOGOUT_REASON_KEY,AUTH_TOKENS_UPDATED_EVENT} from "../context/auth";

const BASE_URL = process.env.REACT_APP_BACKEND_HOST || "http://localhost:8000";
const logout401Message = "Unauthorized (401). User logged out.";

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

// --- Helper function for logout (called by 401 interceptor) ---
// const performLogout = (userMessage = "You have been logged out.") => {
//     console.warn(`performLogout called with userMessage="${userMessage}"`);
//     sessionStorage.setItem(LOGOUT_REASON_KEY, userMessage);
//     // Dispatch event for AuthProvider to clear its state and localStorage
//     window.dispatchEvent(new CustomEvent(AUTH_TOKENS_UPDATED_EVENT, {detail: null}));
// };

// Handles 401 errors for automatic logout
// apiClient.interceptors.response.use(
//     (response) => response,
//     (error) => {
//         const originalRequest = error.config;
//
//         if (error.response && error.response.status === 401) {
//             const noLogoutOn401Paths = [
//                 '/api/v0.2.0/auth/token/', // Login path
//                 // '/api/v0.2.0/auth/refresh/', // Token refresh path
//             ];
//
//             // Check if the request URL is one of the paths where 401 doesn't mean session expiry
//             const isExemptedPath = noLogoutOn401Paths.some(path => originalRequest.url.includes(path));
//
//             if (!isExemptedPath) {
//                 // For any other 401, perform logout
//                 // performLogout("Your session has expired or is invalid. Please log in again.");
//                 // Return a new rejected promise to stop further processing in the original call chain.
//                 // This makes the original API call fail clearly after logout has been initiated.
//                 return Promise.reject(new Error(logout401Message));
//             } else {
//                 console.info(`401 on exempted path (${originalRequest.url}), not performing global logout.`);
//             }
//         }
//         return Promise.reject(error);
//     }
// );

function handleError(error) {
    // if (error.message !== logout401Message) {
    //     console.error("API error:", error.response?.data || error.message || error);
    // }
    throw error;
}

const api = {
    login: async (username, password) => {
        try {
            const res = await apiClient.post(`${BASE_URL}/api/v0.2.0/auth/token/`, {username, password});
            return res.data;
        } catch (err) {
            handleError(err);
        }
    },

    parseDocket: async (formData) => {
        try {
            const res = await apiClient.post(`${BASE_URL}/api/v0.2.0/petition/parse-docket/`, formData);
            return res.data;
        } catch (err) {
            handleError(err);
        }
    },

    generatePetitionBlob: async (petitionFields) => {
        try {
            const res = await apiClient.post(
                `${BASE_URL}/api/v0.2.0/petition/generate/`,
                petitionFields,
                {responseType: "arraybuffer"}
            );
            return new Blob([res.data],
                {type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})
        } catch (err) {
            handleError(err);
        }
    },

    generatePetitionSummaryBlob: async (summary) => {
        try {
            const res = await apiClient.post(
                `${BASE_URL}/api/v0.2.0/petition/generator-report/`,
                summary,
                {responseType: "arraybuffer"}
            );
            return new Blob([res.data],
                {type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})
        } catch (err) {
            handleError(err);
        }
    },

    getAttorneys: async () => {
        try {
            const res = await apiClient.get(`${BASE_URL}/api/v0.2.0/expunger/attorneys/`);
            return res.data;
        } catch (err) {
            handleError(err);
        }
    },

    getAttorney: async (attorney_pk) => {
        try {
            const res = await apiClient.get(`${BASE_URL}/api/v0.2.0/expunger/attorney/${attorney_pk}`);
            return res.data;
        } catch (err) {
            handleError(err);
        }
    },

    updateProfile: async (profileData) => {
        try {
            const res = await apiClient.put(
                `${BASE_URL}/api/v0.2.0/expunger/my-profile/`,
                profileData
            );
            return res;
        } catch (err) {
            handleError(err);
        }
    },

    getUserProfile: async () => {
        try {
            const res = await apiClient.get(`${BASE_URL}/api/v0.2.0/expunger/my-profile/`);
            return res.data;
        } catch (err) {
            handleError(err);
        }
    },
};

export default api;
