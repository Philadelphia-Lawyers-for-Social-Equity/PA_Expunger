import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import api from "../services/api"

import { useAuth } from './auth';

const initialUserState = {
  user: {
    email: "",
    first_name: "",
    last_name: "",
    username: "",
  },
  organization: {
    name: "",
    address: {},
    phone: "",
    pk: -1,
    url: "",
  },
  attorney: {
    bar: "",
    name: "",
    pk: -1,
    url: "",
    user_id: -1,
  }
}

export const UserContext = createContext();

export function useUser() {
  return useContext(UserContext);
}

export function UserProvider({ children }) {
  const { isAuthenticated, authenticatedRequest } = useAuth();
  const [user, setUser] = useState(initialUserState);

  const refreshUserProfile = useCallback(async () => {
    if (isAuthenticated) {
      try {
        const userData = await authenticatedRequest(() => api.getUserProfile());
        setUser(userData);
      } catch (error) {
        setUser(initialUserState);
      }
    } else {
      setUser(initialUserState);
    }
  }, [isAuthenticated, setUser, authenticatedRequest]);

  useEffect(() => {
    async function autoFetchUserProfile() {
      if (isAuthenticated) {
        try {
          const userData = await authenticatedRequest(() => api.getUserProfile());
          setUser(userData);
        } catch (error) {
          setUser(initialUserState);
        }
      } else {
        setUser(initialUserState);
      }
    }

    autoFetchUserProfile();
  }, [isAuthenticated, setUser, authenticatedRequest]);

  const value = { user, setUser, refreshUserProfile };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  )
}
