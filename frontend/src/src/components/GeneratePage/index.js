import React, { useState, useEffect, useReducer } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';

import { Button, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';

/* TODO:
    - Include ratio.
    - Move components to be imported.
*/

const labelWidth = 2;
const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/generate/";
const defaultPetitionFields = {
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

function postRequestConfig() {
    let bearer = "Bearer ";
    let token = bearer.concat(localStorage.getItem("access_token"));
    return {
      'responseType': 'arraybuffer',
      'headers': { 'Authorization': token }
    };
}

function mergeReduce(initial, changes) {
    return({...initial, ...changes});
}

function postGeneratorRequest(petitioner, petition, dockets, charges, restitution) {
    let petitionFields = {
        "petitioner": petitioner,
        "petition": { ...petition, "date": today()},
        "dockets": dockets,
        "charges": charges,
        "restitution": restitution
    }

    console.info(petitionFields);
    axios.post(url, petitionFields, postRequestConfig()).then(
        res => {
            if (res.status === 200) {
                let blob = new Blob([res.data], {type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"});
                let downloadUrl = window.URL.createObjectURL(blob);
                let filename = "petition.docx";
                let disposition = res.headers["content-disposition"];
                let a = document.createElement("a");

                if (typeof a.download === "undefined") {
                  window.location.href = downloadUrl;
                } else {
                  a.href = downloadUrl;
                  a.download = filename;
                  document.body.appendChild(a);
                  a.click();
                }
            }
        }).catch(
            error => {
                console.error(error);
            }
        );
}

export default function GeneratePage(props) {
    /* Props accepts:
        - petitionFields: single petition fields object, as described in the api glossary
    */

    let petitionFields = props.location.state.petitionFields || props.petitionFields || defaultPetitionFields;

    const history = useHistory();

    const [petitioner, setPetitioner] = useReducer(mergeReduce, petitionFields.petitioner);
    const [petition, setPetition] = useReducer(mergeReduce, petitionFields.petition);
    const [dockets, setDockets] = useState(petitionFields.dockets);
    const [charges, setCharges] = useState(petitionFields.charges);
    const [restitution, setRestitution] = useReducer(mergeReduce, petitionFields.restitution);

    return (
        <Form className="generator">
            <Petitioner {... petitioner} handleChange={setPetitioner} />
            <Petition {... petition} handleChange={setPetition} />
            <Dockets dockets={dockets} handleChange={setDockets} />
            <Charges charges={charges} handleChange={setCharges} />
            <Restitution {... restitution} handleChange={setRestitution} />
            <Button onClick={() => { postGeneratorRequest(petitioner, petition, dockets, charges, restitution); }}
            >Generate Petition</Button>
        </Form>

    );
}

function Petitioner(props) {
    /* Props expects:
        - name: string
        - aliases: array of strings
        - dob: iso formatted date string
        - handleChange: function to handle updates

        We don't currently take the address or ssn as arguments because they are
        not available is any of our source data.  Manual entry only.

        Side effects
        - adds address via handleChange
    */

    function aliasItems() {
        if(!props.aliases) {
            return([]);
        }

        return props.aliases.map((a) => ({"text": a, "key": a}));
    }

    function saveAliases(items) {
        let newAliases = items.map((a) => (a.text));
        props.handleChange({"aliases": newAliases});
    }

    return(
        <>
            <h2>Petitioner</h2>
            <GeneratorInput
                label="Full Name"
                type="text"
                placeholder="Full Name"
                name="name"
                value={props.name}
                handleChange={props.handleChange}
                required={true}
            />

            <GeneratorInput
                label="Birth Date"
                type="date"
                name="dob"
                value={props.dob}
                handleChange={props.handleChange}
                required={true}
            />

            <GeneratorInput
                label="Social Security Number"
                type="text"
                placeholder="###-##-####"
                name="ssn"
                value={props.ssn}
                handleChange={props.handleChange}
                required={true}
            />

            <EditableList
                label="Aliases"
                inner={RemovableTextField}
                emptyItem={{"text": "", "key": ""}}
                items={aliasItems()}
                handleChange={(e) => {saveAliases(e)}}
            />

            <Address {... props.address} handleChange={(a) => {props.handleChange({"address": a});}} />
        </>
        );
}

function Address(props) {
    /*
    Props expects:
    - street1
    - street2
    - city
    - state
    - zipcode
    - handleChange: should accept a single address object
    */

    function handleChange(change) {
        let address = {"street1": props.street1, "street2": props.street2, "city": props.city, "state": props.state, "zipcode": props.zipcode};
        let newAddress = mergeReduce(address, change);
        props.handleChange(newAddress);
    }

    return(
        <>
        <GeneratorInput
            label={ <strong>Address</strong> }
            type="text"
            placeholder="Street Address"
            name="street1"
            value={props.street1 || ""}
            handleChange={handleChange}
        />

        <GeneratorInput
            type="text"
            placeholder="Optional Apt/Unit"
            name="street2"
            value={props.street2 || ""}
            handleChange={handleChange}
        />

        <Form.Group as={Row}>
            <Col sm={labelWidth}/>
            <Col sm={4}>
                <Form.Control placeholder="City" value={props.city || ""} onChange={e => {
                    handleChange({"city": e.target.value});
                }} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="State (2-Letter)" value={props.state || ""} onChange={e => {
                    handleChange({"state": e.target.value});
                }} />
            </Col>

            <Col sm={2}>
                <Form.Control placeholder="Zip" value={props.zipcode || ""} onChange={e => {
                    handleChange({"zipcode": e.target.value});
                }} />
            </Col>
        </Form.Group>
        </>
    );
}

function Petition(props) {
    /* props expects:
        - otn
        - dc
        - arrest_date: isoformatted date string, eg "2021-01-29"
        - arrest_officer
        - arrest_agency
        - judge
        - ratio: string, either "partial" or "full"
        - handleChange
    */

    return (
        <>
        <h2>Petition</h2>
        <GeneratorInput
            label="Offense Tracking Number (OTN)"
            type="text"
            placeholder="########" 
            name="otn"
            value={props.otn}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="DC"
            type="text"
            placeholder="########" 
            name="dc"
            value={props.dc}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Arrest Date"
            type="date"
            name="arrest_date"
            value={props.arrest_date}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Arrest Agency"
            type="text"
            placeholder="Arresting Agency"
            name="arrest_agency"
            value={props.arrest_agency}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Arresting Officer"
            type="text"
            placeholder="First & Last Name"
            name="arrest_officer"
            value={props.arrest_officer}
            handleChange={props.handleChange}
        />

        <GeneratorInput
            label="Judge"
            type="text"
            placeholder="First & Last Name"
            name="judge"
            value={props.judge}
            handleChange={props.handleChange}
        />
        <Radio
            label="Is this a full or partial expungement?"
            name="ratio"
            handleChange={props.handleChange}
            items={[["full", "Full Expungement"], ["partial", "Partial Expungement"]]}
            selected={props.ratio || "full"}
        />
        </>
    );
}

function Radio(props) {
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
            <Col sm={labelWidth}>
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

    return (
        <>
            <h2>Restitution</h2>
            <GeneratorInput
                label="Total"
                placeholder="Decimal Number"
                name="total"
                value={props.total || 0}
                handleChange={props.handleChange}
            />
            <GeneratorInput
                label="Paid"
                placeholder="Decimal Number"
                name="paid"
                value={props.paid || 0}
                handleChange={props.handleChange}
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
        - name
        - value
        - handleChange
    */

    if (!props.name) {
        return(<p>Missing name for {props.label}</p>);
    }

    let keyName = props.name;

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
                    onChange={(e) => {
                        let res = {[keyName]: e.target.value};
                        props.handleChange(res);
                    }}
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
        <Row className="mb-2">
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
            <Button
                variant={ hovering ? "danger" : "secondary"}
                onClick={ props.handleRemove }
                cursor="pointer"
            >
                X
            </Button>
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
            className="mb-2"
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
            <Button
                variant={ hovering ? "danger" : "secondary"}
                onClick={ props.handleRemove }
                cursor="pointer"
            >
                X
            </Button>
            </Col>
        </Row>
    );
}

function today() {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0');
    var yyyy = today.getFullYear();
    return(yyyy + '-' + mm + '-' + dd);
}
