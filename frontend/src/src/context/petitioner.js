import React, {createContext, useContext, useEffect, useState} from 'react';
import {AUTH_TOKENS_UPDATED_EVENT} from "./auth";

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

  // Effect to listen for the authTokensUpdated event (e.g., on logout)
    useEffect(() => {
        const handleAuthChange = (event) => {
            // Check if the event signals a logout (tokens are null)
            if (event.detail === null) {
                console.debug('PetitionerProvider: Auth tokens cleared (logout), resetting petitioner data.');
                setPetitioner(initialPetitionerState);
            }
        };

        window.addEventListener(AUTH_TOKENS_UPDATED_EVENT, handleAuthChange);

        // Cleanup listener on component unmount
        return () => {
            window.removeEventListener(AUTH_TOKENS_UPDATED_EVENT, handleAuthChange);
        };
    }, []);

  return (
    <PetitionerContext.Provider value={value}>
      {children}
    </PetitionerContext.Provider>
  )
}
