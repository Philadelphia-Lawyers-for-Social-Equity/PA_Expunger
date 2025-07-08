import React from 'react';
import GeneratorInput from './GeneratorInput'
import { Col, Form, Row } from 'react-bootstrap';

export default function Address(props) {
    /*
    Props expects:
    - street1
    - street2
    - city
    - state
    - zipcode
    - handleChange: should accept a single address object
    */

    function handleChange(change) {
        let address = {"street1": props.street1, "street2": props.street2, "city": props.city, "state": props.state, "zipcode": props.zipcode};
        let newAddress = {...address, ...change};
        props.handleChange(newAddress);
    }

    return(
        <>
        <GeneratorInput
            label="Address"
            type="text"
            placeholder="Street Address"
            name="street1"
            value={props.street1 || ""}
            handleChange={handleChange}
            disabled={props.disabled || false}
            previewComponent={props.previewComponent}
        />

        <GeneratorInput
            type="text"
            placeholder="Optional Apt/Unit"
            name="street2"
            value={props.street2 || ""}
            handleChange={handleChange}
            disabled={props.disabled || false}
            previewComponent={props.previewComponent}
        />

        <Form.Group 
            as={Row}
            className={props.previewComponent ? "p-0 ps-3 pt-2" : "mb-3"}
        >
            <Col sm={2}/>
            <Col sm={4}>
                <Form.Control placeholder="City" value={props.city || ""} onChange={e => {
                    handleChange({"city": e.target.value});
                }}
                    disabled={props.disabled || false} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="State (2-Letter)" value={props.state || ""} onChange={e => {
                    handleChange({"state": e.target.value});
                }}
                    disabled={props.disabled || false} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="Zip" value={props.zipcode || ""} onChange={e => {
                    handleChange({"zipcode": e.target.value});
                }}
                    disabled={props.disabled || false} />
            </Col>
        </Form.Group>
        </>
    );
}
