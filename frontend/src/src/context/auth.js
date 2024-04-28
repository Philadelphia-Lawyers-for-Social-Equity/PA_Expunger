import React, { createContext, useContext, useState } from 'react';

export const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [authTokens, setTokens] = useState(JSON.parse(localStorage.getItem("tokens")) || null);

  function setAuthTokens(tokens) {
    setTokens(tokens)
    localStorage.setItem("tokens", JSON.stringify(tokens));
  }
  function logout() {
    setTokens(null);
    localStorage.removeItem("tokens");
  };

  const value = {
    authTokens, setAuthTokens, logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}