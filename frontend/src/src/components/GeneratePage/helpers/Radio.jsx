import React from 'react';
import { Col, Form, Row } from 'react-bootstrap'; // Form.Check is part of Form

export default function Radio(props) {
    /*
    props expects:
    * label - string title of the entire selection set
    * name - string name for the entire selection set (used for HTML name attribute and for handleChange key)
    * handleChange - function to set the new value; expects an object like {[name]: value}
    * items - array of [value, string_label] combinations
    * selected - value of the currently selected item
    * disabled - boolean, optional
    * controlIdPrefix - string, optional, a prefix for generating unique IDs for Form.Group and Form.Check
    */

    // Use a prefix for controlId and individual check IDs to ensure uniqueness if this component is used multiple times.
    const idPrefix = props.controlIdPrefix || props.name;

    return (
        <Form.Group as={Row} controlId={`${idPrefix}-group`} className="mb-3">
            <Form.Label column sm={2} className="text-top">
                {props.label}
            </Form.Label>
            <Col sm={7} className="d-flex flex-column justify-content-center">
                {(!props.items || props.items.length === 0) && (
                    <Form.Text className="text-muted">No options available.</Form.Text>
                )}
                {props.items && props.items.map((item, idx) => {
                    const itemValue = item[0];
                    const itemLabel = item[1];
                    // Ensure unique ID for each radio button for proper label association
                    const uniqueItemId = `${idPrefix}_${itemValue.toString().replace(/\W/g, '-')}_${idx}`;

                    return (
                        <Form.Check
                            className="my-0"
                            type="radio"
                            key={uniqueItemId}
                            id={uniqueItemId}
                            label={itemLabel}
                            name={props.name}
                            value={itemValue}
                            checked={props.selected === itemValue}
                            onChange={() => {
                                props.handleChange({ [props.name]: itemValue });
                            }}
                            disabled={props.disabled || false}
                        />
                    );
                })}
            </Col>
        </Form.Group>
    );
}
