import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';
import EditableList from '../helpers/EditableList';
import Address from '../helpers/Address';
import RemovableTextField from '../helpers/RemovableTextField';
import SocialSecurityInput from './SocialSecurityInput';
import { usePetitioner } from '../../../context/petitioner.js';

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

    const { petitioner, setPetitioner } = usePetitioner();

    function aliasItems() {
        if(!props.aliases) {
            return([]);
        }

        return props.aliases.map((a, idx) => ({"text": a, "key": `${props.aliases.length}-${idx}`}));
    }

    function saveAliases(items) {
        let newAliases = items.map((a) => (a.text));
        setPetitioner({...petitioner, "aliases": newAliases});
    }

    function handleChange(item) {
        let attribute = Object.keys(item)[0];
        setPetitioner({...petitioner, [attribute]: item[attribute]});
    }

    function showLabel() {
            if (props.preview) {
                return <></>;
            } else {
                return <h2>{props.label}</h2>;
            }
        }

    return(
        <>
            {showLabel()}

            <GeneratorInput
                label="Full Name"
                type="text"
                placeholder="Full Name"
                name="name"
                value={petitioner.name}
                handleChange={handleChange}
                required={true}
                disabled={props.disabled || false}
                previewComponent={props.preview}
            />

            <GeneratorInput
                label="Birth Date"
                type="date"
                name="dob"
                value={petitioner.dob}
                handleChange={handleChange}
                required={true}
                disabled={props.disabled || false}
                previewComponent={props.preview}
            />

            <SocialSecurityInput
                label="Social Security Number"
                type="text"
                placeholder="###-##-####"
                name="ssn"
                value={petitioner.ssn}
                handleChange={handleChange}
                required={true}
                disabled={props.disabled || false}
                previewComponent={props.preview}
            />

            <EditableList
                label="Aliases"
                inner={RemovableTextField}
                emptyItem={{"text": "", "key": ""}}
                items={aliasItems()}
                handleChange={(e) => {saveAliases(e)}}
                disabled={props.disabled || false}
                smallHeader={true}
                previewComponent={props.preview}
            />

            <Address 
                {...petitioner.address} handleChange={(a) => {
                    handleChange({"address": a});
                }} 
                disabled={props.disabled || false} 
                previewComponent={props.preview}
            />
        </>
        );
}
