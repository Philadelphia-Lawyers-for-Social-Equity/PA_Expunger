import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';

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
  const { authTokens } = useAuth();
  const [user, setUser] = useState(initialUserState);

  const value = { user, setUser };

  useEffect(() => {
    function fetchUserData() {
        const token = `Bearer ${authTokens.access}`;
        var config = {
          headers: { Authorization: token },
        };
    
        // Get to return user data
        const url =
          process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/my-profile/";
        axios.get(url, config).then((res) => {
          if (res.status === 200) {
            setUser(res.data);
          }
        })
    }
    if (authTokens) fetchUserData();
  }, [authTokens])

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  )
}