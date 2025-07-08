import React, { createContext, useCallback, useContext, useState, useRef } from 'react';
import { useHistory } from 'react-router-dom';
import api from "../services/api"

export const AuthContext = createContext();
export const TOKEN_STORAGE_KEY = "tokens";
export const LOGOUT_REASON_KEY = "logoutReason";

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({children}) {
    const [authTokens, setTokensState] = useState(() => {
        try {
            const storedTokens = localStorage.getItem(TOKEN_STORAGE_KEY);
            return storedTokens ? JSON.parse(storedTokens) : null;
        } catch (e) {
            console.error("Failed to parse tokens from localStorage during initial state load", e);
            localStorage.removeItem(TOKEN_STORAGE_KEY); // clean corrupted storage
            return null;
        }
    });
    const isLoggingOut = useRef(false);

    const history = useHistory();

    const isAuthenticated = Boolean(authTokens && authTokens.access);

    const setAuthTokens = useCallback((tokens) => {
        if (tokens && tokens.access) { // Ensure tokens object is valid before storing
            localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
            setTokensState(tokens);
            // Also fetch user info here?
        } else {
            localStorage.removeItem(TOKEN_STORAGE_KEY);
            setTokensState(null);
        }
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

    const authenticatedRequest = useCallback(async (apiCall) => {
        if (isLoggingOut.current) {
            return Promise.reject(new Error("Logout in progress."));
        }

        try {
            return await apiCall();
        } catch (error) {
            // Check if the error is a 401 Unauthorized
            if (error.response && error.response.status === 401) {
                // Token refresh handling will go here
                isLoggingOut.current = true;
                logout("Your session has expired. Please log in again.");
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
