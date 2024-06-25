import React from 'react';
import EditableList from '../helpers/EditableList';
import RemovableTextField from '../helpers/RemovableTextField';
import { usePetitions } from '../../../context/petitions';

export default function Dockets({petitionNumber, disabled}) {
    /* props expects:
        - petitionNumber: integer
        - disabled: boolean
    */
    const { petitions, updatePetitions } = usePetitions();
    const docket_numbers = petitions[petitionNumber].docket_numbers;

    function makeItems() {
        return(docket_numbers.map((d) => ({"text": d, "key": d})));
    }

    function handleChange(items) {
        updatePetitions('docket_numbers', petitionNumber, items);
    }

    return (
        <EditableList
            label="Dockets"
            inner={RemovableTextField}
            items={makeItems()}
            emptyItem={{"text": "", "key": ""}}
            handleChange={handleChange}
            disabled={disabled || false}
        />
    );
}
