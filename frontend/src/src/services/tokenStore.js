// Single source of truth for the stored JWT pair. The axios layer refreshes the access
// token on its own, so both it and the auth context read and write through here rather
// than touching localStorage directly, and subscribers hear about every change.

export const TOKEN_STORAGE_KEY = "tokens";

const listeners = new Set();

// For useSyncExternalStore to work properly, getTokens has to return the same object every
// time it's called, unless the stored pair has actually changed.
// We store raw to easily compare if the token has changed (rather than inspecting tokens).
let cache = { raw: null, tokens: null };

export function getTokens() {
    try {
        // Read storage on every call rather than caching on write,
        // in case it was modified in another tab.
        const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (raw !== cache.raw) {
            cache = { raw: raw, tokens: raw ? JSON.parse(raw) : null };
        }
        return cache.tokens;
    } catch (e) {
        console.error("Failed to parse tokens from localStorage", e);
        localStorage.removeItem(TOKEN_STORAGE_KEY); // clean corrupted storage
        cache = { raw: null, tokens: null };
        return null;
    }
}

// Why the pair was last cleared. A code rather than a message: the api layer can tell that
// credentials stopped working, but what the user should be told about it is the auth
// context's call, so the wording lives there.
export const SESSION_ENDED = {
    CREDENTIALS_REJECTED: "credentials-rejected",
    USER_LOGGED_OUT: "user-logged-out",
};

let sessionEndReason = null;

export function getSessionEndReason() {
    return sessionEndReason;
}

// Callers can pass null to clear storage.
export function setTokens(tokens) {
    const storedTokens = tokens && tokens.access ? tokens : null;
    const raw = storedTokens ? JSON.stringify(storedTokens) : null;
    if (raw) {
        localStorage.setItem(TOKEN_STORAGE_KEY, raw);
        sessionEndReason = null; // storing a usable pair means the session is live again
    } else {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
    // Cache the object from the caller, so subscribers and getTokens agree on identity
    cache = { raw: raw, tokens: storedTokens };
    listeners.forEach((listener) => listener(storedTokens));
}

// Clears the pair, recording why. Listeners run before this returns, so one that sees a
// null pair can read getSessionEndReason() to find out what ended the session.
export function clearTokens(reason) {
    sessionEndReason = reason;
    setTokens(null);
}

// Returns teardown (unsubscribe) function
export function subscribeToTokens(listener) {
    listeners.add(listener);
    return () => {
        listeners.delete(listener);
    };
}

// Expiry of a JWT as epoch milliseconds, or null when the token can't be read.
export function getTokenExpiry(token) {
    try {
        const base64urlPayload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(base64urlPayload));
        return typeof payload.exp === "number" ? payload.exp * 1000 : null;
    } catch (e) {
        console.error("Could not read the expiry of a JWT:", e);
        return null;
    }
}
