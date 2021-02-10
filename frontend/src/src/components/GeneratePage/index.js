import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';

import { Button, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';

const labelWidth = 2;

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

    const history = useHistory();

    const [petitioner, setPetitioner] = useState(petitionFields.petitioner);
    const [petition, setPetition] = useState(petitionFields.petition);
    const [dockets, setDockets] = useState(petitionFields.dockets);
    const [charges, setCharges] = useState(petitionFields.charges);
    const [restitution, setRestitution] = useState(petitionFields.restitution);

    return (
        <Form className="generator">
            <Petitioner {... petitioner} handleChange={setPetitioner} />
            <Petition {... petition} handleChange={setPetition} />
            <Dockets dockets={dockets} handleChange={setDockets} />
            <Charges charges={charges} handleChange={setCharges} />
            <Restitution {... restitution} handleChange={setRestitution} />
            <Button onClick={
                () => { console.log({
                    "petitioner": petitioner,
                    "petition": petition,
                    "dockets": dockets,
                    "charges": charges,
                    "restitution": restitution,
                });
            }}
            >Console State</Button>
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
    const [aliases, setAliases] = useState(props.aliases || []);
    const [dob, setDob] = useState(props.dob);

    // We don't currently take the address or ssn as arguments because they are
    // not available is any of our source data.  Manual entry only.
    const [ssn, setSsn] = useState("");
    const [address, setAddress] = useState({"street1": "", "street2": "", "city": "", "state": "", "zipcode": ""});


    function aliasItems() {
        return aliases.map((a) => ({"text": a, "key": a}));
    }

    function saveAliases(items) {
        let newAliases = items.map((a) => (a.text));
        setAliases(newAliases);
    }

    function save() {
        let petitioner = {
            "name": name,
            "aliases": aliases,
            "dob": dob,
            "ssn": ssn,
            "address": address
        };
        props.handleChange(petitioner);
    }

    useEffect(() => {save();}, [name, aliases, dob, ssn, address] );

    return(
        <>
            <h2>Petitioner</h2>

            <GeneratorInput
                label="Full Name"
                type="text"
                placeholder="Full Name"
                value={name}
                handleChange={setName}
            />

            <GeneratorInput
                label="Birth Date"
                type="date"
                value={dob}
                handleChange={setDob}
            />

            <GeneratorInput
                label="Social Security Number"
                type="text"
                placeholder="###-##-####"
                value={ssn}
                handleChange={setSsn}
            /> 

            <EditableList
                label="Aliases"
                inner={RemovableTextField}
                emptyItem={{"text": "", "key": ""}}
                items={aliasItems()}
                handleChange={(e) => {saveAliases(e)}}
            />

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
    const [usState, setUSState] = useState("");
    const [zipcode, setZipCode] = useState("");

    function save() {
        let address = {
            "street1": street1,
            "street2": street2,
            "city": city,
            "state": usState,
            "zipcode": zipcode
        };
        props.handleChange(address);
    }

    useEffect(() => {save();}, [street1, street2, city, usState, zipcode]);

    return(
        <>
        <GeneratorInput
            label={ <strong>Address</strong> }
            type="text"
            placeholder="Street Address"
            value={street1}
            handleChange={setStreet1}
        />

        <GeneratorInput
            type="text"
            placeholder="Optional Apt/Unit"
            value={street2}
            handleChange={setStreet2}
        />

        <Form.Group as={Row} controlId="formPlaintextCityStateZip">
            <Col sm={labelWidth}/>
            <Col sm={4}>
                <Form.Control placeholder="City" value={city} onChange={e => {
                    setCity(e.target.value);
                }} />
            </Col>

            <Col sm={labelWidth}>
                <Form.Control placeholder="State (2-Letter)" value={usState} onChange={e => {
                    setUSState(e.target.value);
                }} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="Zip" value={zipcode} onChange={e => {
                    setZipCode(e.target.value);
                }} />
            </Col>
        </Form.Group>
        </>
    );
}

function Petition(props) {
    /* props expects:
        - otn: string
        - dc: string
        - arrest_date: isoformatted date string, eg "2021-01-29"
        - arrest_officer: string
        - arrest_agency: string
        - judge: string, should be the full name of the judge
        - ratio: string, either "partial" or "full"
        - handleChange(petition): function should accept a single object
    */

    const [otn, setOtn] = useState(props.otn);
    const [dc, setDc] = useState(props.dc);
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

    useEffect(() => {save();}, [otn, dc, arrestDate, arrestOfficer, arrestAgency, judge, ratio]);

    return (
        <>
        <h2>Petition</h2>
        <GeneratorInput
            label="Offense Tracking Number (OTN)"
            type="text"
            placeholder="########" 
            value={otn}
            handleChange={setOtn}
        />

        <GeneratorInput
            label="DC"
            type="text"
            placeholder="########" 
            value={dc}
            handleChange={setDc}
        />

        <GeneratorInput
            label="Arrest Date"
            type="date"
            value={arrestDate}
            handleChange={setArrestDate}
        />

        <GeneratorInput
            label="Arrest Agency"
            type="text"
            placeholder="Arresting Agency"
            value={arrestAgency}
            handleChange={setArrestAgency}
        />

        <GeneratorInput
            label="Arresting Officer"
            type="text"
            placeholder="First & Last Name"
            value={arrestOfficer}
            handleChange={setArrestOfficer}
        />

        <GeneratorInput
            label="Judge"
            type="text"
            placeholder="First & Last Name"
            value={judge}
            handleChange={setJudge}
        />
        </>
    );
}

function Dockets(props) {
    /* props expects:
        - dockets: a list of docket strings
        - handleChange: function should accept a list of docket strings and do the update
    */

    const [dockets, setDockets] = useState(props.dockets);

    function makeItems() {
        return(dockets.map((d) => ({"text": d, "key": d})));
    }

    function saveItems(items) {
        let newDockets = items.map((item) => (item.text));
        setDockets(newDockets);
    }

    function save(){
        props.handleChange(dockets);
    }

    useEffect(() => {save();}, [dockets]);

    return (
        <EditableList
            label="Dockets"
            inner={RemovableTextField}
            items={makeItems()}
            emptyItem={{"text": "", "key": ""}}
            handleChange={(e) => {saveItems(e);}}
        />
    );
}

function Charges(props) {
    /* props expects:
        - charges: list of charge objects, per the api glossary or Charge props
        - handleChange: function should take a list of charge objects, handle the update
    */

    const [charges, setCharges] = useState(props.charges);

    function makeItems() {
        return(charges.map((c) => ({...c, "key": c.description})));
    }

    function saveItems(items) {
        items.map((obj) => {delete obj.key;});
        setCharges(items);
    }

    function save() { props.handleChange(charges); }

    useEffect(() => {save()}, [charges]);

    return (
        <EditableList
            label="Charges"
            inner={RemovableCharge}
            items={makeItems()}
            emptyItem={{"statute": "", "description": "", "grade": "", "date": "", "disposition": "", "key": ""}}
            handleChange={(e) => {saveItems(e);}}
        />
    );
}

function Restitution(props) {
    /* props expects:
        - total: decimal number
        - paid: decimal number
        - handleChange
    */

    const [total, setTotal] = useState(props.total || "");
    const [paid, setPaid] = useState(props.paid || "");

    function save() {
        let newTotal = parseFloat(total);
        let newPaid = parseFloat(paid);

        props.handleChange({"total": newTotal, "paid": newPaid});
    }

    useEffect(() => {save();}, [total, paid]);

    // Stub
    return (
        <>
            <h2>Restitution</h2>
            <GeneratorInput
                label="Total"
                placeholder="Decimal Number"
                value={total}
                handleChange={setTotal}
            />
            <GeneratorInput
                label="Paid"
                placeholder="Decimal Number"
                value={paid}
                handleChange={setPaid}
            />
        </>
    );
}


function GeneratorInput(props) {
    /* A typical label + value pair for this page's single-row inputs.

        props expects:
        - label
        - type: html5 input type
        - placeholder
        - value
        - handleChange
    */

    return (
        <Form.Group as={Row}>
            <Col sm={labelWidth}>
                <Form.Label>{props.label}</Form.Label>
            </Col>
            <Col sm={8}>
                <Form.Control
                    type={props.type}
                    placeholder={props.placeholder}
                    value={props.value || ""}
                    onChange={(e) => { props.handleChange(e.target.value); }}
                />
            </Col>
        </Form.Group>
    );
}

function EditableList(props) {
    /* Turn a list of property objects into specified items, including widgets
       to add or remove extra items

        props expects:
            - label
            - inner: the Inner component to attach to each property.  Should
              accept a "key" argument or provide its own index.
            - emptyItem: property object template for a new item
            - items: array of property objects appropriate for Inner component
            - handleChange
    */

    const Inner = props.inner;
    const [showAddButton, setShowAddButton] = useState(true);

    function addItem() {
        let arr = props.items.slice();
        arr.push(props.emptyItem);
        props.handleChange(arr);
    }

    function updateItem(idx, newItem) {
        let arr = props.items.slice();
        arr.splice(idx, 1, newItem);
        props.handleChange(arr);
    }

    function dropItem(idx) {
        let arr = props.items.slice();
        arr.splice(idx, 1);
        console.log("Dropped item: " + idx);
        props.handleChange(arr);
    }

    function isEmpty(obj) {
        let objString = JSON.stringify(obj);
        let emptyString = JSON.stringify(props.emptyItem);
        console.log("Compare " + objString + " " + emptyString);
        return(objString == emptyString);
    }

    function AddButton() {
        let variant = "primary";
        let onClick = () => {addItem()};

        if (props.items.length > 0 && isEmpty(props.items.slice(-1)[0])) {
            variant = "secondary"
            onClick = null;
        }
        return(
            <Button
                variant={variant}
                onClick={onClick}
            >Add { props.label }</Button>
        );
    }
    
    return (
        <Form.Group as="div">
            { props.label ? <h2>{props.label}</h2> : <></> }
            { props.items.map((innerProps, idx) => {
                    return(
                        <Inner
                            {... innerProps}
                            handleChange={(txt) => {updateItem(idx, txt);}}
                            handleRemove={() => { dropItem(idx);}}
                />);
            })}

            <Row>
                <Col sm={labelWidth}/>
                <Col className="text-left" sm={8}>
                    <AddButton />
                </Col>
            </Row>
        </Form.Group>
    );

}

function RemovableCharge(props) {
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
        <Row>
            <Col sm={labelWidth}><Form.Label>{props.label || ""}</Form.Label></Col>
            <Col sm={2}>
                <Form.Control
                    placeholder="Statute"
                    value={statute}
                    onChange={(e) => {setStatute(e.target.value);}}
                    readOnly={!editing}
                />
            </Col>
            <Col sm={1}>
                <Form.Control
                    placeholder="grade"
                    value={grade}
                    onChange={(e) => {setGrade(e.target.value);}}
                    readOnly={!editing}
                />
            </Col>
            <Col sm={2}>
                <Form.Control
                    type="date"
                    value={date}
                    onChange={(e) => {setDate(e.target.value);}}
                    readOnly={!editing}
                />
            </Col>
            <Col sm={2}>
                <Form.Control
                    placeholder="Disposition"
                    value={disposition}
                    onChange={(e) => {setDisposition(e.target.value);}}
                    readOnly={!editing}
                />
            </Col>
            <Col sm={1}>
                { hovering
                    ?  <Button
                            variant="danger"
                            onClick={ props.handleRemove }
                            cursor="pointer"
                        >X</Button>
                    : <></> 
                }
            </Col>
        </Row>
        <Row>
            <Col sm={labelWidth}></Col>
            <Col sm={7}>
                <Form.Control
                    value={description}
                    onChange={(e) => {setDescription(e.target.value);}}
                    readOnly={!editing}
                />
            </Col>
        </Row>
        <Row><Col sm={labelWidth}/><Col sm={8}><hr /></Col></Row>
        </div>
    );
}


function RemovableTextField(props) {

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
        >
            <Col sm={labelWidth}>
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
            />
            </Col>
            <Col sm={1}>
                { hovering
                    ?  <Button
                            variant="danger"
                            onClick={ props.handleRemove }
                            cursor="pointer"
                        >X</Button>
                    : <></> 
                }
            </Col>
        </Row>
    );
}
