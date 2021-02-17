import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';
import Radio from '../helpers/Radio';

export default function Petition(props) {
    /* props expects:
        - otn
        - dc
        - arrest_date: isoformatted date string, eg "2021-01-29"
        - arrest_officer
        - arrest_agency
        - judge
        - ratio: string, either "partial" or "full"
        - handleChange
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
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="DC"
            type="text"
            placeholder="########" 
            name="dc"
            value={props.dc}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Arrest Date"
            type="date"
            name="arrest_date"
            value={props.arrest_date}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Arrest Agency"
            type="text"
            placeholder="Arresting Agency"
            name="arrest_agency"
            value={props.arrest_agency}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Arresting Officer"
            type="text"
            placeholder="First & Last Name"
            name="arrest_officer"
            value={props.arrest_officer}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Judge"
            type="text"
            placeholder="First & Last Name"
            name="judge"
            value={props.judge}
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