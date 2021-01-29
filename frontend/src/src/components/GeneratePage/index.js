import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';

import { Button, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';

export default function GeneratePage(props) {
    /* Props accepts:
        - petitionFields: single petition fields object, as described in the api glossary
    */

    let defaultPetitionFields = {
        "petitioner": {
            "name": "",
            "aliases": [],
            "dob": ""
        },
        "petition": {
            "otn": "",
            "arrest_date": "",
            "arrest_officer": "",
            "arrest_agency": "",
            "judge": "",
            "ratio": "full",
        },
        "dockets": [],
        "charges": [],
        "restitution": {
            "total": 0,
            "paid": 0
        }
    }

    let petitionFields = props.location.state.petitionFields || props.petitionFields || defaultPetitionFields;

    console.debug("Petition Fields");
    const history = useHistory();

    const [petitioner, setPetitioner] = useState(petitionFields.petitioner);
    const [petition, setPetition] = useState(petitionFields.petition);
    const [dockets, setDockets] = useState(petitionFields.dockets);
    const [charges, setCharges] = useState(petitionFields.charges);
    const [restitution, setRestitution] = useState(petitionFields.restitution);

    return (
        <Form>
            <Petitioner {... petitioner} handleChange={setPetitioner} />
            <Petition {... petition} handleChange={setPetition} />
            <Dockets dockets={dockets} handleChange={setDockets} />
            <Charges charges={charges} handleChange={setCharges} />
            <Restitution {... restitution} handleChange={setRestitution} />
        </Form>
    );
}

function Petitioner(props) {
    /* Props expects:
        - name: string
        - aliases: array of strings
        - dob: iso formatted date string
        - handleChange: function to handle updates

        Side effects
        - adds address via handleChange
    */

    const [name, setName] = useState(props.name);
    const [aliases, setAliases] = useState(props.aliases);
    const [dob, setDob] = useState(props.dob);
    const [ssn, setSsn] = useState("");

    const [address, setAddress] = useState({"street1": "", "street2": "", "city": "", "state": "", "zipcode": ""});

    function save() {
        props.handleChange({
            "name": name,
            "aliases": aliases,
            "dob": dob,
            "ssn": ssn,
            "address": address
        });
    }

    return(
        <>
            <Form.Group as={Row}>
                <Col sm={3}><Form.Label>Full Name</Form.Label></Col>

                <Col md={{ span: 8 }}>
                    <Form.Control placeholder="Full Name" value={name} onChange={e => {
                        setName(e.target.value);
                        save();
                    }} />
                </Col>
            </Form.Group>

            <Form.Group as={Row} controlId="formPlaintextSSNum">
                <Col sm={3}><Form.Label>Social Security</Form.Label></Col>

                <Col sm="6">
                    <Form.Control placeholder="###-##-####" value={ssn} onChange={e => {
                        setSsn(e.target.value);
                        save();
                    }} />
                </Col>
            </Form.Group>

            <Address handleChange={setAddress} />
        </>
        );
}

function Address(props) {
    /*
    Props expects:
    - handleChange: function to handle updates
    */

    const [street1, setStreet1] = useState("");
    const [street2, setStreet2] = useState("");
    const [city, setCity] = useState("");
    const [usState, setState] = useState("");
    const [zipcode, setZipcode] = useState("");

    function save() {
        props.handleChange({
            "street1": street1,
            "street2": street2,
            "city": city,
            "state": usState,
            "zipcode": zipcode
        });
    }

    return(
        <>
        <Form.Group as={Row} controlId="formPlaintextAddress">
            <Col sm={3}>
                <Form.Label>
                    <strong>Address</strong>
                </Form.Label>
            </Col>

            <Col sm="8">
                <Form.Control placeholder="Street Address" value={street1} onChange={e => {
                    setStreet1(e.target.value);
                    save();
                }} />
            </Col>

            <Col sm="8">
                <Form.Control placeholder="Optional Apt/Unit" value={street2} onChange={e => {
                    setStreet2(e.target.value);
                    save();
                }} />
            </Col>
        </Form.Group>

        <Form.Group as={Row} controlId="formPlaintextCityStateZip">

            <Col sm={4}>
                <Form.Control placeholder="City" value={city} onChange={e => {
                    setCity(e.target.value);
                    save();
                }} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="State (2-Letter)" value={usState} onChange={e => {
                    setState(e.target.value);
                    save();
                }} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="Zip" value={zipcode} onChange={e => {
                    setZipcode(e.target.value);
                    save();
                }} />
            </Col>
        </Form.Group>
        </>
    );
}

function Petition(props) {
    /* props expects:
        - otn: string
        - arrest_date: isoformatted date string, eg "2021-01-29"
        - arrest_officer: string
        - arrest_agency: string
        - judge: string, should be the full name of the judge
        - ratio: string, either "partial" or "full"
        - handleChange(petition): function should accept a single object
    */

    const [otn, setOtn] = useState(props.otn);
    const [arrestDate, setArrestDate] = useState(props.arrest_date);
    const [arrestOfficer, setArrestOfficer] = useState(props.arrest_date);
    const [arrestAgency, setArrestAgency] = useState(props.arrest_date);
    const [judge, setJudge] = useState(props.judge);
    const [ratio, setRatio] = useState(props.ratio);

    function save() {
        props.handleChange({
            "otn": otn,
            "arrest_date": arrestDate,
            "arrest_officer": arrestOfficer,
            "arrest_agency": arrestAgency,
            "judge": judge,
            "ratio": ratio
        });
    }

    // Stub
    return (
        <div>
            <h2>Petition</h2>
            <ul>
                <li>otn: {otn}</li>
                <li>arrestDate: {arrestDate}</li>
                <li>arrestAgency: {arrestAgency}</li>
                <li>judge: {judge}</li>
                <li>ratio: {ratio}</li>
            </ul>
        </div>
    );
}

function Dockets(props) {
    /* props expects:
        - dockets: a list of docket strings
        - handleChange: function should accept a list of docket strings and do the update
    */

    const [dockets, setDockets] = useState(props.dockets);

    function save() { props.handleChange(dockets); }

    // Stub
    return (
        <div>
            <h2>Dockets</h2>
            <ol>
                { dockets.map((docket, key) => (<li key={key}>{docket}</li>)) }
            </ol>
        </div>
    );
}

function Charges(props) {
    /* props expects:
        - charges: list of charge objects, per the api glossary or Charge props
        - handleChange: function should take a list of charge objects, handle the update
    */

    const [charges, setCharges] = useState(props.charges);
    function save() { props.handleChange(charges) };

    // Stub
    return (
        <div>
            <h2>Charges</h2>
            <ul>
                { charges.map((charge, key) => ( <li>{ JSON.stringify(charge) }</li> ))}
            </ul>
        </div>
    );
}

function Restitution(props) {
    /* props expects:
        - total: decimal number
        - paid: decimal number
        - handleChange: function should take a total and paid argument, handle the update
    */

    const [total, setTotal] = useState(props.total);
    const [paid, setPaid] = useState(props.paid);

    function save() { props.handleChange(total, paid); }

    // Stub
    return (
        <div>
            <h2>Restitution</h2>
            <ul>
                <li>Total: {total}</li>
                <li>Paid: {paid}</li>
            </ul>
        </div>
    );
}
