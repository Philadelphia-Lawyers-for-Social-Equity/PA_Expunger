import React, {createContext, useContext, useEffect, useState} from "react";
import {useAuth} from "./auth";

export const initialPetitionState = {
    petitions: [
        {
            charges: [],
            docket_info: {
                otn: '',
                complaint_date: '',
                judge: '',
                ratio: ''
            },
            docket_numbers: [],
            fines: {
                total: 0,
                paid: 0
            }
        }
    ],
}

export const PetitionsContext = createContext();

export function usePetitions() {
    return useContext(PetitionsContext);
}

export function PetitionsProvider({children}) {
    const [petitions, setPetitions] = useState(initialPetitionState);
    const [petitionNumber, setPetitionNumber] = useState(0)
    const {isAuthenticated} = useAuth();

    useEffect(() => {
        if (!isAuthenticated) {
            if (petitions !== initialPetitionState || petitionNumber !== 0) {
                setPetitions(initialPetitionState);
                setPetitionNumber(0);
            }
        }
    }, [isAuthenticated, petitions, petitionNumber]);


    // Effect to listen for the authTokensUpdated event (e.g., on logout)
    // useEffect(() => {
    //     const handleAuthChange = (event) => {
    //         // Check if the event signals a logout (tokens are null)
    //         if (event.detail === null) {
    //             console.debug('PetitionsProvider: Auth tokens cleared (logout), resetting petitions data.');
    //             setPetitions(initialPetitionState);
    //             setPetitionNumber(0);
    //         }
    //     };
    //
    //     window.addEventListener(AUTH_TOKENS_UPDATED_EVENT, handleAuthChange);
    //
    //     // Cleanup listener on component unmount
    //     return () => {
    //         window.removeEventListener(AUTH_TOKENS_UPDATED_EVENT, handleAuthChange);
    //     };
    // }, []);

    function updatePetitions(field, petitionNumber, changes) {
        if (['docket_info', 'fines'].includes(field)) {
            let attribute = Object.keys(changes)[0];
            setPetitions(currPetitions => currPetitions.map((petition, index) => {
                if (index === petitionNumber) {
                    return ({
                        ...petition,
                        [field]: {
                            ...petition[field],
                            [attribute]: changes[attribute]
                        }
                    })
                } else return petition
            }))
        } else if (['charges', 'docket_numbers'].includes(field)) {
            let newDockets = (field === 'docket_numbers') ? changes.map((item) => (item.text)) : null;
            setPetitions(currPetitions => currPetitions.map((petition, index) => {
                if (index === petitionNumber) {
                    return ({
                        ...petition,
                        [field]: newDockets || changes
                    })
                } else return petition
            }))
        }
    }

    const value = {
        petitions,
        setPetitions,
        petitionNumber,
        setPetitionNumber,
        updatePetitions
    };

    return (
        <PetitionsContext.Provider value={value}>
            {children}
        </PetitionsContext.Provider>
    )
}
