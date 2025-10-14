import React, { createContext, useContext, useRef, useCallback } from 'react';

const NavBlockContext = createContext();

export function useNavBlock() {
  return useContext(NavBlockContext);
}

export function NavBlockProvider({ children }) {
  const blockNavRef = useRef(false);

  const setBlockNav = useCallback((isBlocked) => {
    blockNavRef.current = isBlocked;
  }, []);

  const value = { blockNavRef, setBlockNav };

  return (
    <NavBlockContext.Provider value={value}>
      {children}
    </NavBlockContext.Provider>
  );
}
