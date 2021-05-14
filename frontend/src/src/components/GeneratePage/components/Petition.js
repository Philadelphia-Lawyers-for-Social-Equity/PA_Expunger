import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';
import Radio from '../helpers/Radio';

export default function Petition(props) {
    /* 
    props expects:
        - otn
        - judge
        - ratio: string, either "partial" or "full"
        - handleChange
    props also includes (but does not use):
        - dc
        - arrest_date: isoformatted date string, eg "2021-01-29"
        - arrest_officer
        - arrest_agency
    */

    return (
        <>
        <h2>Petition</h2>
        <GeneratorInput
            label="Offense Tracking Number (OTN)"
            type="text"
            placeholder="########"
            name="otn"
            value={props.otn}
            errorMsg={props.errorReport['petition.otn']}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Judge"
            type="text"
            placeholder="First & Last Name"
            name="judge"
            value={props.judge}
            errorMsg={props.errorReport['petition.judge']}
            handleChange={props.handleChange}
        />
        <Radio
            label="Is this a full or partial expungement?"
            name="ratio"
            handleChange={props.handleChange}
            items={[["full", "Full Expungement"], ["partial", "Partial Expungement"]]}
            selected={props.ratio || "full"}
        />
        </>
    );
}
