import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';
import Radio from '../helpers/Radio';
import { requiredInputValidators } from '../helpers/validatorUtils';

const sectionKey = 'petition';

export default function Petition(props) {
    /* props expects:
        - otn
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
                disabled={props.disabled || false}
                required={true}
                validator={requiredInputValidators[sectionKey]['otn'].validator}
            />
            <GeneratorInput
                label="Judge"
                type="text"
                placeholder="First & Last Name"
                name="judge"
                value={props.judge}
                handleChange={props.handleChange}
                disabled={props.disabled || false}
                required={true}    
                validator={requiredInputValidators[sectionKey]['judge'].validator}
            />
            <Radio
                label="Is this a full or partial expungement?"
                name="ratio"
                handleChange={props.handleChange}
                items={[
                    ["full", "Full Expungement"],
                    ["partial", "Partial Expungement"],
                ]}
                selected={props.ratio || "full"}
                disabled={props.disabled || false}
            />
        </>
    );
}
