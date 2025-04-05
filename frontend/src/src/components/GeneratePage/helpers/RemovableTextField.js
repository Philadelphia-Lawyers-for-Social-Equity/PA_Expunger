import React, { useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';

export default function RemovableTextField(props) {

    /* Produce an individually editable text item
        props expects
        - label
        - text
        - handleChange
        - handleRemove
        - disabled
    */

    const [text, setText] = useState(props.text);
    const [hovering, setHovering] = useState(false);

    function save() {
        props.handleChange({"text": text});
    }

    function handleEnterKey(press) {
        if (press.key === "Enter") {
            save();
        }
    }

    return(
        <Row
            className="mb-2"
        >
            <Col sm={2}>
                <Form.Label>
                    { props.label }
                </Form.Label>
            </Col>
            <Col sm={7}>
            <Form.Control
                onChange={e => { setText(e.target.value)}}
                onBlur={() => save()}
                onKeyDown={(e) => {handleEnterKey(e)}}
                value={text}
                disabled={ props.disabled || false }
            />
            </Col>
            <Col sm={1}>
            <Button
                variant={ hovering ? "danger" : "secondary"}
                onClick={ props.handleRemove }
                cursor="pointer"
                disabled={ props.disabled || false }
                onMouseOver={() => setHovering(true)}
                onMouseOut={() => setHovering(false)}
            >
                X
            </Button>
            </Col>
        </Row>
    );
}