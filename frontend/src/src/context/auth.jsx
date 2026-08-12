import React, { createContext, useCallback, useContext, useEffect, useSyncExternalStore } from 'react';
import { useHistory } from 'react-router-dom';
import api from "../services/api"
import {
    clearTokens,
    getSessionEndReason,
    getTokenExpiry,
    getTokens,
    SESSION_ENDED,
    setTokens,
    subscribeToTokens
} from "../services/tokenStore";

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
    // The axios layer refreshes tokens on its own, so subscribe to the store rather than
    // keeping a copy here that can fall behind what is stored.
    const authTokens = useSyncExternalStore(subscribeToTokens, getTokens);

    const history = useHistory();

    const isAuthenticated = Boolean(authTokens && authTokens.access);

    // The api layer drops the pair when the server stops accepting it, which is all it is
    // in a position to know. Deciding what that means for the user is this layer's job, so
    // the wording lives here. Subscribing rather than watching isAuthenticated in an effect
    // keeps this ahead of the redirect: it runs inside clearTokens, before React re-renders
    // and PrivateRoute sends anyone to the login page to read the message.
    useEffect(() => subscribeToTokens((tokens) => {
        if (!tokens && getSessionEndReason() === SESSION_ENDED.CREDENTIALS_REJECTED) {
            sessionStorage.setItem(LOGOUT_REASON_KEY, SESSION_EXPIRED_MESSAGE);
        }
    }), []);

    const login = useCallback(async (username, password) => {
        try {
            const tokens = await api.login(username, password);
            setTokens(tokens);
        } catch (error) {
            console.error("Login failed:", error);
            throw error;
        }
    }, []);

    // Handles intentional user logout.
    const logout = useCallback((userMessage) => {
        sessionStorage.setItem(LOGOUT_REASON_KEY, userMessage);
        clearTokens(SESSION_ENDED.USER_LOGGED_OUT);
    }, [history]);

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
                    // A refusal of the token itself has already cleared the pair, which
                    // unwinds the session on its own. Still holding one means the failure
                    // was something else — a network drop, a refusal from in front of the
                    // backend — so keep trying rather than letting the session lapse.
                    if (getTokens()) {
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
    }, [authTokens]);

    // Callers just call api.* directly. A 401 that survives the api layer means the refresh
    // was refused, and refusing it already cleared the pair — which drops isAuthenticated,
    // redirects through PrivateRoute, and leaves the message above for the login page. There
    // is nothing left for a wrapper here to add, and a wrapper that treated every 401 as a
    // dead session would end one that a network blip had only interrupted.
    const value = {
        isAuthenticated,
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}
