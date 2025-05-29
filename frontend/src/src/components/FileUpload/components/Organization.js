import React from "react";
import { Card, Col, Row } from 'react-bootstrap';

export default function Organization(props) {
    /*
        props expects:
        - organization
    */
    const { name, address } = props.organization;

    const orgAddress = address.stree2 
        ? `${address.street1}, ${address.street2}` 
        : address.street1;

    return (
        <Card className="mb-4">
            <Card.Header as="h5" className="pl-3">
                Organization
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
                        Address
                    </Col>
                    <Col sm={8}>
                        <Row>{orgAddress}</Row>
                        <Row>{`${address.city}, ${address.state} ${address.zipcode}`}</Row>
                    </Col>
                </Row>
            </Card.Body>
        </Card>
    )

}