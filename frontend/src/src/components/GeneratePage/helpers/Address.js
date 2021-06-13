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

    const hasErrors =
        props.errorReport["petitioner.address"] != null
            || props.errorReport["petitioner.address.street1"] != null
            || props.errorReport["petitioner.address.city"] != null
            || props.errorReport["petitioner.address.state"] != null
            || props.errorReport["petitioner.address.zipcode"] != null;

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
            errorMsg={props.errorReport['petitioner.address.street1']}
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
                onChange={e => {handleChange({"city": e.target.value});}}
                isInvalid={props.errorReport["petitioner.address.city"] != null}
            />
            </Col>

            <Col sm={2}>
            <Form.Control
                placeholder="State (2-Letter)"
                value={props.state || ""} onChange={e => {
                handleChange({"state": e.target.value});
                }}
                isInvalid={props.errorReport["petitioner.address.state"] != null}
                />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="Zip" value={props.zipcode || ""} onChange={e => {
                    handleChange({"zipcode": e.target.value});
                 }}
                    isInvalid={props.errorReport["petitioner.address.zipcode"] != null}
            />
            </Col>
        </Form.Group>
<Row>
<Col sm={2}/>
<Col>
            <AddressError showMessage={ hasErrors }/>
</Col>
</Row>
        </>
    );
}


function AddressError(props) {
    /*
     Props expects:
     - showMessage
    */
        if (props.showMessage) {
            return(<p style={{color: "red"}}>Please fix the address.</p>); } else { return(<></>); }
    }
