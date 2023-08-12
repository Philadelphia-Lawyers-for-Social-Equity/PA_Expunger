import React from 'react';
import { Col, Form, Row } from 'react-bootstrap';

export default function GeneratorInput(props) {
    /* A typical label + value pair for this page's single-row inputs.

        props expects:
        - label
        - type: html5 input type
        - placeholder
        - name
        - value
        - handleChange

        optional props:
        - required (boolean)
        - validator (function)
    */

    if (!props.name) {
        return(<p>Missing name for {props.label}</p>);
    }

    let keyName = props.name;
    const optionalValidationProps =
        props.required && props.validator ?
            { required: true, isValid: props.validator(props.value), isInvalid: !props.validator(props.value) } :
            {};

    return (
        <Form.Group as={Row}>
            <Col sm={2}>
                <Form.Label>{props.label}</Form.Label>
            </Col>
            <Col sm={8}>
                <Form.Control
                    type={props.type}
                    placeholder={props.placeholder}
                    value={props.value || ""}
                    onChange={(e) => {
                        let res = {[keyName]: e.target.value};
                        props.handleChange(res);
                    }}
                    {...optionalValidationProps}
                />
            </Col>
        </Form.Group>
    );
}
