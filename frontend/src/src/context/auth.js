import React, { createContext, useContext, useState } from 'react';

export const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [authTokens, setAuthTokens] = useState(null);

  function logout () {
    setAuthTokens(null);
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