import React from "react";
import { Card, Col, Row } from 'react-bootstrap';

export default function Attorney(props) {
    /*
        props expects:
        - attorney
    */
    const { name, bar } = props.attorney;

    return (
        <Card className="mb-4">
            <Card.Header as="h5" className="ps-3">
                Attorney
            </Card.Header>
            <Card.Body>
                <Row>
                    <Col sm={2}>
                        Name
                    </Col>
                    <Col sm={8} className="p-0">
                        {name}
                    </Col>
                </Row>
                <Row>
                    <Col sm={2}>
                        Bar Number
                    </Col>
                    <Col sm={8}>
                        <Row>{bar}</Row>
                    </Col>
                </Row>
            </Card.Body>
        </Card>
    )
}
