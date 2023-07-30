import React from 'react';
import GeneratorCurrencyInput from '../helpers/GeneratorCurrencyInput';

export default function Restitution(props) {
  /* props expects:
        - total: decimal number
        - paid: decimal number
        - handleChange
    */

  return (
    <>
      <h2>Restitution</h2>
      <GeneratorCurrencyInput
        label="Total"
        placeholder="Total fines and fees"
        name="total"
        value={props.total}
        handleChange={props.handleChange}
      />
      <GeneratorCurrencyInput
        label="Paid"
        placeholder="Amount paid"
        name="paid"
        value={props.paid}
        handleChange={props.handleChange}
      />
    </>
  );
}
