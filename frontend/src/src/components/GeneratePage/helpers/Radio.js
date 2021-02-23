import React from 'react';
import { Col, Row } from 'react-bootstrap';

export default function Radio(props) {
    /* Build a radio selection

    props expects:
    * label - string title of the entire selection set
    * name - string name for the entire selection set
    * handleChange - function to set the new value
    * items - array of [value, string] combinations, that will build each
    * selected - value of checked item
    */

    function RadioOption(props) {
        /* Build a radio option

        * label
        * name
        * value
        * handleChange
        * checked - boolean
        */

        let itemId = props.name + props.value;
        let name = props.name

        return (
            <li>
                <input type="radio" name={name} id={itemId}
                    value={props.value} className="form-check-input"
                    defaultChecked={props.checked}
                    onChange={() => { props.handleChange({[name]: props.value}); }}
                />
                <label htmlFor={ itemId } className="form-check-label">{props.label}</label>
            </li>
        );
    }

    return(
        <Row>
            <Col sm={2}>
                {props.label}
            </Col>
            <Col>
                <ul>
                    { props.items.map((item, idx) => (
                        <RadioOption
                            key={item[0]}
                            label={item[1]}
                            name={props.name}
                            value={item[0]}
                            handleChange={props.handleChange}
                            checked={item[0] === props.selected}
                        />
                    ))}
                </ul>
            </Col>
        </Row>
    );
}
