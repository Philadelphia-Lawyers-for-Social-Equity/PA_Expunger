import React, { createContext, useContext, useState } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [tokenTime, setTokenTime] = useState(localStorage.getItem('time') || null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access') || null);
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh') || null);
  const authedAxios = axios.create({
    baseURL: `${process.env.REACT_APP_BACKEND_HOST}/api/v0.2.0`,
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  authedAxios.interceptors.request.use(async function (config) {
    const timePassed = Date.now() - tokenTime;
    
    // if 10 min since access token set
    if ( timePassed > 60000 ) {
      const verifyResponse = await axios.post(
        `${process.env.REACT_APP_BACKEND_HOST}/api/v0.2.0/auth/verify/`,
        { token: refreshToken },
      );

      const refreshTokenIsVerified = Object.keys(verifyResponse.data).length === 0;

      if ( refreshTokenIsVerified ) {
        const refreshResponse = await axios.post(
          `${process.env.REACT_APP_BACKEND_HOST}/api/v0.2.0/auth/refresh/`,
          { refresh: refreshToken }
        );

        const newAccessToken = refreshResponse.data.access;

        setAccessToken(newAccessToken);
        localStorage.setItem('access', newAccessToken);

        const now = Date.now();
        setTokenTime(now);
        localStorage.setItem('time', now);

        config.headers.Authorization = `Bearer ${newAccessToken}`;
        return config;
      } else {
        logout();
      }
    }
    
    return config;
  });

  function updateAccessToken(token) {
    const now = Date.now()
    
    setTokenTime(now);
    localStorage.setItem('time', now)
    
    setAccessToken(token);
    localStorage.setItem('access', token);
  }

  function updateRefreshToken(token) {
    setRefreshToken(token);
    localStorage.setItem('refresh', token);
  }

  function logout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setAccessToken(null);
    setRefreshToken(null);
  };

  const value = {
    accessToken,
    refreshToken,
    authedAxios,
    updateAccessToken,
    updateRefreshToken,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
