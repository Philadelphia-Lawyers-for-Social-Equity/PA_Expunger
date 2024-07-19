import React from 'react';
import GeneratorCurrencyInput from '../helpers/GeneratorCurrencyInput';
import { usePetitions } from '../../../context/petitions';

export default function Fines({petitionNumber, disabled}) {
    /* props expects:
        - petitionNumber: integer
        - disabled: boolean
    */
    const { petitions, updatePetitions } = usePetitions();
    const fines = petitions[petitionNumber].fines;

    function handleChange(fine) {
      updatePetitions('fines', petitionNumber, fine)
    }

    return (
        <>
            <h2>Fines & Fees</h2>
            <GeneratorCurrencyInput
                label="Total"
                placeholder="Total fines and fees"
                name="total"
                value={fines.total}
                handleChange={handleChange}
                disabled={disabled || false}
                petitionNumber={petitionNumber}
            />
            <GeneratorCurrencyInput
                label="Paid"
                placeholder="Amount paid"
                name="paid"
                value={fines.paid}
                handleChange={handleChange}
                disabled={disabled || false}
                petitionNumber={petitionNumber}
            />
        </>
    );
}
