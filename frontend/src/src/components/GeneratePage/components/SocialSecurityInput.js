import React, { Component } from 'react';
import GeneratorInput from '../helpers/GeneratorInput';

class SocialSecurityInput extends Component {

  formatSSN(value) {
    const cleaned = ('' + value).replace(/\D/g, '');
    const match = cleaned.match(/^(\d{0,3})(\d{0,2})(\d{0,4})$/);
    if (match) {
      return (!match[2] ? match[1] : `${match[1]}-${match[2]}`) + (match[3] ? `-${match[3]}` : '');
    }
    return value;
  }

  handleInputChange = (v) => {
    const formattedValue = this.formatSSN(v.ssn);
    this.props.handleChange(v, formattedValue);
  }

  render() {
    const { label, type, placeholder, name, value, required, disabled } = this.props;
    const formattedSSN = this.formatSSN(value);
    return (
      <GeneratorInput
        label={label}
        type={type}
        placeholder={placeholder}
        name={name}
        value={formattedSSN}
        handleChange={this.handleInputChange}
        required={required}
        maxLength={5}
        disabled={disabled}
      />
    );
  }
}

export default SocialSecurityInput;
