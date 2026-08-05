// Single source of truth for the stored JWT pair. The axios layer refreshes the access
// token on its own, so both it and the auth context read and write through here rather
// than touching localStorage directly, and subscribers hear about every change.

export const TOKEN_STORAGE_KEY = "tokens";

const listeners = new Set();

export function getTokens() {
    try {
        const storedTokens = localStorage.getItem(TOKEN_STORAGE_KEY);
        return storedTokens ? JSON.parse(storedTokens) : null;
    } catch (e) {
        console.error("Failed to parse tokens from localStorage", e);
        localStorage.removeItem(TOKEN_STORAGE_KEY); // clean corrupted storage
        return null;
    }
}

// Anything without an access token clears storage, so passing null logs the session out.
export function setTokens(tokens) {
    const storedTokens = tokens && tokens.access ? tokens : null;
    if (storedTokens) {
        localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(storedTokens));
    } else {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
    listeners.forEach((listener) => listener(storedTokens));
}

// Returns the function that unsubscribes again.
export function subscribeToTokens(listener) {
    listeners.add(listener);
    return () => {
        listeners.delete(listener);
    };
}

// Expiry of a JWT as epoch milliseconds, or null when the token can't be read.
export function getTokenExpiry(token) {
    try {
        const encodedPayload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(encodedPayload));
        return typeof payload.exp === "number" ? payload.exp * 1000 : null;
    } catch (e) {
        console.error("Could not read the expiry of a JWT:", e);
        return null;
    }
}
