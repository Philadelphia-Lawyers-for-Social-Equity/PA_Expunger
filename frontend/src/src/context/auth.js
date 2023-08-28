import { createContext, useContext } from 'react';

export const AuthContext = createContext({
  authTokens: null,
  setAuthTokens: () => {},
  logout: () => {}
});

export function useAuth() {
  return useContext(AuthContext);
}
