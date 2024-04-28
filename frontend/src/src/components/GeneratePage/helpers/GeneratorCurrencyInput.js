import React from 'react';
import { Col, Form, Row } from 'react-bootstrap';
import CurrencyInput from 'react-currency-input-field';

export default function GeneratorCurrencyInput(props) {
  /* A typical label + value pair for this page's single-row inputs.

        props expects:
        - label
        - type: html5 input type
        - placeholder
        - name
        - value
        - handleChange
    */

  if (!props.name) {
    return <p>Missing name for {props.label}</p>;
  }

  let keyName = props.name;

  return (
    <Form.Group as={Row}>
      <Col sm={2}>
        <Form.Label>{props.label}</Form.Label>
      </Col>
      <Col sm={8}>
        <CurrencyInput
          allowNegativeValue={false}
          className="form-control"
          decimalsLimit={2}
          decimalScale={2}
          defaultValue={props.value}
          label="Total"
          onValueChange={(value, _, values) => {
            const changeObj = {};
            changeObj[keyName] = values.float.toFixed(2);
            props.handleChange(changeObj);
          }}
          placeholder={props.placeholder}
          prefix="$"
          disabled={props.disabled || false}
        />
      </Col>
    </Form.Group>
  );
}
