import React, { createContext, useCallback, useContext, useEffect, useState, useRef } from 'react';
import { useHistory } from 'react-router-dom';
import api from "../services/api"
import { getTokenExpiry, getTokens, setTokens, subscribeToTokens } from "../services/tokenStore";

export const AuthContext = createContext();
export const LOGOUT_REASON_KEY = "logoutReason";
export const SESSION_EXPIRED_MESSAGE = "Your session has expired. Please log in again.";

// Refresh this far ahead of the access token's expiry, so no request goes out carrying a
// token that expires while it is in flight.
const REFRESH_LEAD_MS = 60 * 1000;
// Floor on the scheduling delay: without it a very short access token lifetime would turn
// the refresh loop into a request storm.
const MIN_REFRESH_DELAY_MS = 5 * 1000;
// setTimeout treats anything past this as zero, which would do the same.
const MAX_REFRESH_DELAY_MS = 2 ** 31 - 1;
// A refresh that failed without a response was a network problem, not an expired session,
// so back off and try again rather than throwing the user out.
const REFRESH_RETRY_DELAY_MS = 30 * 1000;

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({children}) {
    const [authTokens, setTokensState] = useState(getTokens);
    const isLoggingOut = useRef(false);

    const history = useHistory();

    const isAuthenticated = Boolean(authTokens && authTokens.access);

    // The axios layer refreshes tokens on its own, so follow the store rather than
    // assuming what is in state is still what is stored.
    useEffect(() => subscribeToTokens(setTokensState), []);

    const setAuthTokens = useCallback((tokens) => {
        setTokens(tokens); // the subscription above feeds this back into state
    }, []);

    const login = useCallback(async (username, password) => {
        try {
            const tokens = await api.login(username, password);
            setAuthTokens(tokens);
            isLoggingOut.current = false;
        } catch (error) {
            console.error("Login failed:", error);
            throw error;
        }
    }, [setAuthTokens]);

    // Handles intentional user logout.
    const logout = useCallback((userMessage) => {
        sessionStorage.setItem(LOGOUT_REASON_KEY, userMessage);
        setAuthTokens(null);
        history.push("/login");
    }, [setAuthTokens, history]);

    // Keep the access token fresh for as long as the app is open. A successful refresh
    // replaces authTokens, which re-runs this effect and schedules the next one.
    useEffect(() => {
        const accessToken = authTokens?.access;
        if (!accessToken) {
            return;
        }
        const expiry = getTokenExpiry(accessToken);
        if (expiry === null) {
            return; // Unreadable token: fall back to refreshing when a request gets a 401.
        }

        let timer = null;
        let cancelled = false;

        const scheduleRefresh = (delay) => {
            timer = setTimeout(async () => {
                try {
                    await api.refreshTokens();
                } catch (error) {
                    if (cancelled) {
                        return;
                    }
                    if (error.response) {
                        logout(SESSION_EXPIRED_MESSAGE);
                    } else {
                        console.error("Scheduled token refresh failed:", error);
                        scheduleRefresh(REFRESH_RETRY_DELAY_MS);
                    }
                }
            }, delay);
        };

        const untilRefresh = expiry - REFRESH_LEAD_MS - Date.now();
        scheduleRefresh(Math.min(Math.max(untilRefresh, MIN_REFRESH_DELAY_MS), MAX_REFRESH_DELAY_MS));

        return () => {
            cancelled = true;
            clearTimeout(timer);
        };
    }, [authTokens, logout]);

    const authenticatedRequest = useCallback(async (apiCall) => {
        if (isLoggingOut.current) {
            return Promise.reject(new Error("Logout in progress."));
        }

        try {
            return await apiCall();
        } catch (error) {
            // A 401 here means the api layer already tried to refresh and could not, so
            // the session is genuinely over.
            if (error.response && error.response.status === 401) {
                isLoggingOut.current = true;
                logout(SESSION_EXPIRED_MESSAGE);
            }
            throw error;
        }
    }, [logout]);

    const value = {
        isAuthenticated,
        login,
        logout,
        authenticatedRequest
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}
