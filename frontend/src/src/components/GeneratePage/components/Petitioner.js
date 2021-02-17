import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';
import EditableList from '../helpers/EditableList';
import Address from '../helpers/Address';

export default function Petitioner(props) {
    /* Props expects:
        - name: string
        - aliases: array of strings
        - dob: iso formatted date string
        - handleChange: function to handle updates

        We don't currently take the address or ssn as arguments because they are
        not available is any of our source data.  Manual entry only.

        Side effects
        - adds address via handleChange
    */

    function aliasItems() {
        if(!props.aliases) {
            return([]);
        }

        return props.aliases.map((a) => ({"text": a, "key": a}));
    }

    function saveAliases(items) {
        let newAliases = items.map((a) => (a.text));
        props.handleChange({"aliases": newAliases});
    }

    return(
        <>
            <h2>Petitioner</h2>
            <GeneratorInput
                label="Full Name"
                type="text"
                placeholder="Full Name"
                name="name"
                value={props.name}
                handleChange={props.handleChange}
                required={true}
            />

            <GeneratorInput
                label="Birth Date"
                type="date"
                name="dob"
                value={props.dob}
                handleChange={props.handleChange}
                required={true}
            />

            <GeneratorInput
                label="Social Security Number"
                type="text"
                placeholder="###-##-####"
                name="ssn"
                value={props.ssn}
                handleChange={props.handleChange}
                required={true}
            />

            <EditableList
                label="Aliases"
                inner={RemovableTextField}
                emptyItem={{"text": "", "key": ""}}
                items={aliasItems()}
                handleChange={(e) => {saveAliases(e)}}
            />

            <Address {... props.address} handleChange={(a) => {props.handleChange({"address": a});}} />
        </>
        );
}
