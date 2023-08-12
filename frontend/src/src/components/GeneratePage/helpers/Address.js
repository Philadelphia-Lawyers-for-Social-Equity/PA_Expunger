import React from 'react';
import GeneratorInput from './GeneratorInput';
import { Col, Form, Row } from 'react-bootstrap';
import { addressValidators } from './validatorUtils';

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
            label={ <strong>Address</strong> }
            type="text"
            placeholder="Street Address"
            name="street1"
            value={props.street1 || ""}
            handleChange={handleChange}
            required={true}
            validator={addressValidators['street1'].validator}
        />

        <GeneratorInput
            type="text"
            placeholder="Optional Apt/Unit"
            name="street2"
            value={props.street2 || ""}
            handleChange={handleChange}
        />

        <Form.Group as={Row}>
            <Col sm={2}/>
            <Col sm={4}>
                <Form.Control
                    placeholder="City"
                    value={props.city || ""}
                    onChange={e => {
                        handleChange({"city": e.target.value});
                    }}
                    required={true}
                    isValid={addressValidators['city'].validator(props.city)}
                    isInvalid={!addressValidators['city'].validator(props.city)}
                />
            </Col>

            <Col sm={2}>
                <Form.Control
                    placeholder="State (2-Letter)"
                    value={props.state || ""}
                    onChange={e => {
                        handleChange({"state": e.target.value});
                    }}
                    required={true}
                    isValid={addressValidators['state'].validator(props.state)}
                    isInvalid={!addressValidators['state'].validator(props.state)}
                />
            </Col>

            <Col sm={2}>
                <Form.Control
                    placeholder="Zip"
                    value={props.zipcode || ""}
                    onChange={e => {
                        handleChange({"zipcode": e.target.value});
                    }}
                    required={true}
                    isValid={addressValidators['zipcode'].validator(props.zipcode)}
                    isInvalid={!addressValidators['zipcode'].validator(props.zipcode)}
                />
            </Col>
        </Form.Group>
        </>
    );
}
