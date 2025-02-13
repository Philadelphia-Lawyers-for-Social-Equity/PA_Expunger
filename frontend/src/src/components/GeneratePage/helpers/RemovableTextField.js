import React, { useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';

export default function RemovableTextField(props) {

    /* Produce an individually editable text item
        props expects
        - label
        - text
        - handleChange
        - handleRemove
    */

    const [text, setText] = useState(props.text);
    const [editing, setEditing] = useState(false);
    const [hovering, setHovering] = useState(false);

    function save() {
        setEditing(false);
        props.handleChange({"text": text, "key": text});
    }

    function handleEnterKey(press) {
        if (editing && press.key === "Enter") {
            save();
        }
    }

    return(
        <Row
            onMouseOver={() => setHovering(true)}
            onMouseOut={() => setHovering(false)}
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
                onFocus={() => setEditing(true)}
                onBlur={() => save()}
                onKeyDown={(e) => {handleEnterKey(e)}}
                value={text}
                readOnly={ !editing }
                disabled={ props.disabled || false }
            />
            </Col>
            <Col sm={1}>
            <Button
                variant={ hovering ? "danger" : "secondary"}
                onClick={ props.handleRemove }
                cursor="pointer"
                disabled={ props.disabled || false }
            >
                X
            </Button>
            </Col>
        </Row>
    );
}