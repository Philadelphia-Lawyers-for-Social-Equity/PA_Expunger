import React, { useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';

export default function RemovableCharge(props) {
    /* props expects:
        - label
        - statute
        - description
        - grade
        - date
        - disposition
        - handleChange
        - handleRemove

    */

    const [statute, setStatute] = useState(props.statute || "");
    const [description, setDescription] = useState(props.description || "");
    const [grade, setGrade] = useState(props.grade || "");
    const [date, setDate] = useState(props.date || "");
    const [disposition, setDisposition] = useState(props.disposition || "");

    const [editing, setEditing] = useState(false);
    const [hovering, setHovering] = useState(false);

    function save() {
        props.handleChange({
            "statute": statute,
            "description": description,
            "grade": grade,
            "date": date,
            "disposition": disposition,
            "key": description
        });
        setEditing(false);
    }

    return (
        <div
            onMouseOver={() => {setHovering(true);}}
            onMouseOut={() => {setHovering(false);}}
            onFocus={() => {setEditing(true);}}
            onBlur={() => {save();}}
        >
        <Row className="mb-2">
            <Col sm={2}><Form.Label>{props.label || ""}</Form.Label></Col>
            <Col sm={2}>
                <Form.Control
                    placeholder="Statute"
                    value={statute}
                    onChange={(e) => {setStatute(e.target.value);}}
                    readOnly={!editing}
                    disabled={props.disabled || false}
                />
            </Col>
            <Col sm={1}>
                <Form.Control
                    placeholder="grade"
                    value={grade}
                    onChange={(e) => {setGrade(e.target.value);}}
                    readOnly={!editing}
                    disabled={props.disabled || false}
                />
            </Col>
            <Col sm={2}>
                <Form.Control
                    type="date"
                    value={date}
                    onChange={(e) => {setDate(e.target.value);}}
                    readOnly={!editing}
                    disabled={props.disabled || false}
                />
            </Col>
            <Col sm={2}>
                <Form.Control
                    placeholder="Disposition"
                    value={disposition}
                    onChange={(e) => {setDisposition(e.target.value);}}
                    readOnly={!editing}
                    disabled={props.disabled || false}
                />
            </Col>
            <Col sm={1}>
            <Button
                variant={ hovering ? "danger" : "secondary"}
                onClick={ props.handleRemove }
                cursor="pointer"
                disabled={props.disabled || false}
            >
                X
            </Button>
            </Col>
        </Row>
        <Row>
            <Col sm={2}></Col>
            <Col sm={7}>
                <Form.Control
                    value={description}
                    onChange={(e) => {setDescription(e.target.value);}}
                    readOnly={!editing}
                    disabled={props.disabled || false}
                />
            </Col>
        </Row>
        <Row><Col sm={2}/><Col sm={8}><hr /></Col></Row>
        </div>
    );
}
