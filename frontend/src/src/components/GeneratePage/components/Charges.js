import React from 'react';
import EditableList from '../helpers/EditableList';
import RemovableCharge  from '../helpers/RemovableCharge';

export default function Charges(props) {
    /* props expects:
        - charges: list of charge objects, per the api glossary or Charge props
        - handleChange: function should take a list of charge objects, handle the update
    */

    return (
        <EditableList
            label="Charges"
            inner={RemovableCharge}
            items={props.charges}
            emptyItem={{"statute": "", "description": "", "grade": "", "date": "", "disposition": "", "key": ""}}
            handleChange={props.handleChange}
            disabled={props.disabled || false}
            smallHeader={false}
        />
    );
}
