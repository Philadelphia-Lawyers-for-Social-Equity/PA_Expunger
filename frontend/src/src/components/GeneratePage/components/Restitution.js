import React from 'react';
import GeneratorInput from '../helpers/GeneratorInput';

export default function Restitution(props) {
    /* props expects:
        - total: decimal number
        - paid: decimal number
        - handleChange
    */

    return (
        <>
            <h2>Restitution</h2>
            <GeneratorInput
                label="Total"
                placeholder="Decimal Number"
                name="total"
                value={props.total || 0}
                handleChange={props.handleChange}
            />
            <GeneratorInput
                label="Paid"
                placeholder="Decimal Number"
                name="paid"
                value={props.paid || 0}
                handleChange={props.handleChange}
            />
        </>
    );
}
