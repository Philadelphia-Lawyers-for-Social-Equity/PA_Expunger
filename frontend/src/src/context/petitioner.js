import React, { createContext, useContext, useState } from 'react';

export const PetitionerContext = createContext();

export function usePetitioner() {
  return useContext(PetitionerContext);
}

export function PetitionerProvider({ children }) {
  const [petitionerData, setPetitionerData] = useState({});

  const value = { petitionerData, setPetitionerData };

  return (
    <PetitionerContext.Provider value={value}>
      {children}
    </PetitionerContext.Provider>
  )
}
