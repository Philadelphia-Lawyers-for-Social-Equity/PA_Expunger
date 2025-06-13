import React from 'react';
import EditableList from '../helpers/EditableList';
import RemovableCharge  from '../helpers/RemovableCharge';
import { usePetitions } from '../../../context/petitions';

export default function Charges({petitionNumber, disabled}) {
    /* props expects:
        - petitionNumber: integer
        - disabled: boolean
    */
    const { petitions, updatePetitions } = usePetitions();
    
    const charges = petitions[petitionNumber].charges.map((charge, idx) => {
        const key = `${petitions[petitionNumber].charges.length}-${idx}`
        charge["key"] = key;
        return charge
    });

    function handleChange(newCharges) {
        updatePetitions('charges', petitionNumber, newCharges)
    }

    return (
        <EditableList
            label="Charges"
            inner={RemovableCharge}
            items={charges}
            emptyItem={{"statute": "", "description": "", "grade": "", "date": "", "disposition": "", "key": ""}}
            handleChange={handleChange}
            disabled={disabled || false}
        />
    );
}
