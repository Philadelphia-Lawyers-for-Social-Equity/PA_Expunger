import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from "./auth";

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

export function PetitionerProvider({children}) {
  const [petitioner, setPetitioner] = useState(initialPetitionerState);
  const {isAuthenticated} = useAuth();


  useEffect(() => {
    if (!isAuthenticated) {
      if (petitioner !== initialPetitionerState) {
        setPetitioner(initialPetitionerState);
      }
    }
  }, [isAuthenticated, petitioner, setPetitioner]);

  const value = { petitioner, setPetitioner };

  return (
    <PetitionerContext.Provider value={value}>
      {children}
    </PetitionerContext.Provider>
  )
}
