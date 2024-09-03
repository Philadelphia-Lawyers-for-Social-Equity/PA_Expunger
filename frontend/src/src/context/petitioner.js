import React, { createContext, useContext, useState } from 'react';

export const PetitionerContext = createContext();

export function usePetitioner() {
  return useContext(PetitionerContext);
}

export const initialPetitionerState = {
  preferred_name: "",
  name: "",
  aliases: [],
  dob: "",
  ssn: "",
  address: "",
}

export function PetitionerProvider({ children }) {
  const [petitioner, setPetitioner] = useState(initialPetitionerState);

  const value = { petitioner, setPetitioner };

  return (
    <PetitionerContext.Provider value={value}>
      {children}
    </PetitionerContext.Provider>
  )
}
