import React, {createContext, useCallback, useContext, useEffect, useState} from 'react';

export const AuthContext = createContext();
export const TOKEN_STORAGE_KEY = "tokens";
export const LOGOUT_REASON_KEY = "logoutReason";

export const AUTH_TOKENS_UPDATED_EVENT = 'authTokensUpdated';

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

    // Handles intentional user logout.
    const logout = useCallback((userMessage = "You have successfully logged out.") => {
        sessionStorage.setItem(LOGOUT_REASON_KEY, userMessage);
        setAuthTokens(null);

        window.dispatchEvent(new CustomEvent(AUTH_TOKENS_UPDATED_EVENT, {detail: null}));
    }, [setAuthTokens]);

    // Subscribes to the global 'authTokensUpdated' window event.
    // This event is dispatched when auth tokens are externally modified.
    // It allows AuthProvider to synchronize its state (and localStorage via setAuthTokens)
    // with these changes. `event.detail` will be the new tokens object or null for logout.
    useEffect(() => {
        const handleExternalTokenUpdate = (event) => {
            console.log(`AuthContext: Received ${AUTH_TOKENS_UPDATED_EVENT} event.`, event.detail);
            if (event.detail === null) {
                setAuthTokens(null);
            } else if (event.detail && event.detail.access) { // Check for valid token structure
                setAuthTokens(event.detail);
            }
        };

        window.addEventListener(AUTH_TOKENS_UPDATED_EVENT, handleExternalTokenUpdate);

        // cleanup
        return () => {
            window.removeEventListener(AUTH_TOKENS_UPDATED_EVENT, handleExternalTokenUpdate);
        };
    }, [setAuthTokens]);

    const value = {
        authTokens,
        setAuthTokens,
        isAuthenticated,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}
