import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';
import Radio from '../helpers/Radio';
import { requiredInputValidators } from '../helpers/validatorUtils';

const sectionKey = 'petition';

export default function Petition(props) {
    /* props expects:
        - otn
        - dc
        - complaint_date: isoformatted date string, eg "2021-01-29"
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
            required={true}
            validator={requiredInputValidators[sectionKey]['otn'].validator}
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
            label="Complaint Date"
            type="date"
            name="complaint_date"
            value={props.complaint_date}
            handleChange={props.handleChange}
            required={true}    
            validator={requiredInputValidators[sectionKey]['complaint_date'].validator}
            />

        <GeneratorInput
            label="Arrest Agency"
            type="text"
            placeholder="Arresting Agency"
            name="arrest_agency"
            value={props.arrest_agency}
            handleChange={props.handleChange}
            required={true}    
            validator={requiredInputValidators[sectionKey]['arrest_agency'].validator}
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
            required={true}    
            validator={requiredInputValidators[sectionKey]['judge'].validator}
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