import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';
// import { useAuth } from '../../context/auth';


export default function GeneratePage() {

    const history = useHistory();
    const [isError2, setIsError2] = useState(false);
    const [dataReady, setDataReady] = useState(false);

    /* Petitioner */
    const [fullName, setFullName] = useState("");
    const [aliases, setAliases] = useState([]);
    const [dob, setDOB] = useState("");
    const [street1, setStreet1] = useState("");
    const [street2, setStreet2] = useState("");
    const [city, setCity] = useState("");
    const [twoLetterState, setTwoLetterState] = useState("");
    const [zipcode, setZipcode] = useState("");
    const [ssn, setSSN] = useState("");

    /* Petition */
    const [otn, setOTN] = useState("");
    const [dc, setDC] = useState("");
    const [arrestAgency, setArrestAgency] = useState("");
    const [arrestDate, setArrestDate] = useState("");
    const [arrestOfficer, setArrestOfficer] = useState("");
    const [judge, setJudge] = useState("");
    const [dockets, setDockets] = useState([]);
    const [restitutionTotal, setRestitutionTotal] = useState(0.0);
    const [restitutionPaid, setRestitutionPaid] = useState(0.0);
    const [ratio, setChargeRatio] = useState("full"); // may only be "full" or "partial"

    /* Charges */
    const [charges, setCharges] = useState({});
    const [checkedItems, setCheckedItems] = useState({});


    // useEffect is the React Hook equivalent to ComponentDidMount
    useEffect(() => {
        const localdocketdata = JSON.parse(localStorage.getItem("docketdata"));
        setDockets(localdocketdata.dockets);
        setFullName(localdocketdata.petitioner.name);
        setCharges(localdocketdata.charges);
        setAliases(localdocketdata.petitioner.aliases);
        setDOB(localdocketdata.petitioner.dob);
        setOTN(localdocketdata.petition.otn);
        setArrestAgency(localdocketdata.petition.arrest_agency);
        setArrestDate(localdocketdata.petition.arrest_date);
        setArrestOfficer(localdocketdata.petition.arrest_officer);
        setJudge(localdocketdata.petition.judge);
        setChargeRatio(localdocketdata.petition.ratio);
        if (JSON.stringify(localdocketdata.restitution) !== JSON.stringify({})) {
            setRestitutionTotal(localdocketdata.restitution.total.toFixed(2));
            setRestitutionPaid(localdocketdata.restitution.paid.toFixed(2));
        }
        //missing DC number (pending update from Pablo)
        // setDC(res.data.petition.dc);

        setDataReady(true);

    }, []); // empty array as the second argument will limit to one get call

    // On click for the cancel button
    function returnToChooseAction() {
        history.push("/action");
    }                

    // checkboxes onchange for charges table
    function handleCheckbox(target) {
        setCheckedItems({...checkedItems, [target.name] : target.checked});
    }

     // On click to check that the manual entry fields are filled
    function checkInfo() {

    if (street1 === "" || city === "" || twoLetterState === "" || zipcode === "" || ssn === "") {
      setIsError2(true);
    }
    else {
      postToGeneratePetition();
    }
  }

  function postToGeneratePetition() {

    var newCharges = [];

    for (var i = 0; i < charges.length; i++) {
        if(!document.getElementById(i.toString()).children[0].checked) {
            newCharges.push(charges[i]);
        };
    }

    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0');
    var yyyy = today.getFullYear();
    today = yyyy + '-' + mm + '-' + dd;

    const realData = {
      "petitioner": {
        "name": fullName,
        "aliases": aliases,
        "dob": dob,
        "ssn": ssn,
        "address": {
          "street1": street1,
          "street2": street2,
          "city": city,
          "state": twoLetterState,
          "zipcode": zipcode
        }
      },
      "petition": {
        "date": today,
        "petition_type": "expungement",
        "ratio": ratio,
        "otn": otn,
        "dc": dc,
        "arrest_agency": arrestAgency,
        "arrest_date": arrestDate,
        "arrest_officer": arrestOfficer,
        "judge": judge
      },
      "charges" : newCharges,
      "dockets": dockets,
      "restitution": {
        "total": parseFloat(restitutionTotal),
        "paid": parseFloat(restitutionPaid)
      }
    }

    // Header for POST call
    const bearer = "Bearer ";
    const token = bearer.concat(localStorage.getItem("access_token"));
    var config = {
      'responseType': 'arraybuffer',
      'headers': { 'Authorization': token }
    };

    const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/generate/";

    axios.post(url, realData, config)
      .then(
        res => {
          if (res.status === 200) {
            let blob = new Blob([res.data], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }),
              downloadUrl = window.URL.createObjectURL(blob),
              filename = "petition.docx",
              disposition = res.headers["content-disposition"];

            let a = document.createElement("a");
            if (typeof a.download === "undefined") {
              window.location.href = downloadUrl;
            } else {
              a.href = downloadUrl;
              a.download = filename;
              document.body.appendChild(a);
              a.click();
            }
          } //close res status 200
        } //close res
      ); //close then
  } //close post call function

    return (
        <div className="text-center">
            {dataReady && <div>

                <Row style={{ margin: `80px` }}>


                    <Col md={{ span: 8, offset: 2 }}>

                        <p>Please manually enter the client's Address and Social Security Number</p>
                        <Form>
                        <Form.Group as={Row} controlId="formPlaintextAddress">
                                <Col sm={3}>
                                    <Form.Label>
                                        <strong>Address</strong>
                                    </Form.Label>
                                </Col>
                                <Col sm="8">
                                    <Form.Control placeholder="Street Address" value={street1} onChange={e => {
                                        setStreet1(e.target.value);
                                    }} />
                                </Col>
                                <Col sm={3}>
                                    <Form.Label>
                                    </Form.Label>
                                </Col>
                                <Col sm="8">
                                    <Form.Control placeholder="Optional Apt/Unit" value={street2} onChange={e => {
                                        setStreet2(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row} controlId="formPlaintextCityStateZip">
                                <Col sm={3}>
                                    <Form.Label>
                                    </Form.Label>
                                </Col>
                                <Col sm={4}>
                                    <Form.Control placeholder="City" value={city} onChange={e => {
                                        setCity(e.target.value);
                                    }} />
                                </Col>
                                <Col sm={2}>
                                    <Form.Control placeholder="State (2-Letter)" value={twoLetterState} onChange={e => {
                                        setTwoLetterState(e.target.value);
                                    }} />
                                </Col>
                                <Col sm={2}>
                                    <Form.Control placeholder="Zip" onChange={e => {
                                        setZipcode(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row} controlId="formPlaintextSSNum">
                                <Col sm={3}>
                                    <Form.Label>
                                        <strong>Social Security</strong>
                                    </Form.Label>
                                </Col>
                                <Col sm="6">
                                    <Form.Control placeholder="###-##-####" onChange={e => {
                                        setSSN(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}></Form.Group>
                            <Form.Group as={Row}></Form.Group>

                            <p>The fields below were pulled from the docket. Please review and only make corrections if necessary. </p>

                            <EditableListText
                                label="Dockets"
                                items={ dockets ? dockets : [] }
                                handleUpdate={ setDockets }
                            />

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Full Name
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="Full Name" value={fullName} onChange={e => {
                                        setFullName(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <EditableListText
                                label="Aliases"
                                items={ aliases ? aliases : [] }
                                handleUpdate={ setAliases }
                            />

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Date of Birth
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 3 }}>
                                    <Form.Control placeholder="mm-dd-yyyy" value={dob} onChange={e => {
                                        setDOB(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>


                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        OTN Number
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="########" value={otn} onChange={e => {
                                        setOTN(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        DC
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="########" value={dc} onChange={e => {
                                        setDC(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Arrest Date
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="mm-dd-yyyy" value={arrestDate} onChange={e => {
                                        setArrestDate(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Arrest Agency
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="Arresting Agency" value={arrestAgency} onChange={e => {
                                        setArrestAgency(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Arrest Officer
                                </Form.Label>
                                </Col>
                                <Col sm="8">
                                    <Form.Control placeholder="First Last" value={arrestOfficer} onChange={e => {
                                        setArrestOfficer(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Full Name of Judge
                                </Form.Label>
                                </Col>
                                <Col sm="8">
                                    <Form.Control placeholder="First Last" value={judge} onChange={e => {
                                        setJudge(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Restitution Amount
                                    </Form.Label>
                                </Col>
                                <Col sm={4}>
                                    Total <Form.Control placeholder="Total" id="totalRestitution" value={restitutionTotal} onChange={e => {
                                        setRestitutionTotal(e.target.value);
                                    }} />
                                </Col>
                                <Col sm={4}>
                                    Paid <Form.Control placeholder="Paid" id="paidRestitution" value={restitutionPaid} onChange={e => {
                                        setRestitutionPaid(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>



                            <Row>
                                <Col>
                                    <Table>
                                        <thead>
                                            <tr>
                                                <th>Statute</th>
                                                <th>Date</th>
                                                <th>Grade</th>
                                                <th>Description</th>
                                                <th>Disposition</th>
                                                <th>Remove Charge from Petition</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {charges.map((charge, index) => (<tr key={index}>
                                                <td className="statute">{charge.statute}</td>
                                                <td className="date">{charge.date}</td>
                                                <td className="grade">{charge.grade}</td>
                                                <td className="description">{charge.description}</td>
                                                <td className="disposition">{charge.disposition}</td>
                                                <td><ToggleButton type="checkbox" variant="dark" id={index} value={index} name={index} checked={checkedItems[index]} onChange={e => { handleCheckbox(e.target); }} /></td>
                                            </tr>))}
                                        </tbody>
                                    </Table>
                                </Col>
                            </Row>

                            <Form.Group as={Row}></Form.Group>

                            <Row>
                                <Col sm={3}>
                                </Col>
                                <Col sm={6}>
                                    <Radio
                                        label="Is this a full or partial expungement?"
                                        name="chargeRatio"
                                        handleChange={setChargeRatio}
                                        items={[["full", "Full Expungement"], ["partial", "Partial Expungement"]]}
                                        selected={ratio}
                                    />
                                </Col>
                                <Col sm={3}>
                                </Col>
                            </Row>

                            <Row>
                                <Col sm={3}>
                                </Col>
                                <Col sm={6}>
                                    
                                    <Button id="ExpungeButton" onClick={checkInfo}>Expunge</Button>
                                    {isError2 && <div>Please enter client address and social security number</div>}
                                </Col>
                                <Col sm={3}>
                                </Col>
                            </Row>
                            <Row>
                                <Col>
                                <Button id="cancelButton" onClick={returnToChooseAction}>Cancel</Button>
                                </Col>
                            </Row>
                        </Form>

                    </Col>

                </Row>

            </div>}

        </div >
    );
}


/* Produce an editable list of text items.

    props requires:
    * label - name / title of the list
    * items - array of strings
    * handleUpdate - function should take a new list of strings,   update parent
      state
*/

function EditableListText(props) {

    function addItem() {
        let arr = props.items.slice();
        arr.push("");
        props.handleUpdate(arr);
    }

    function updateItem(idx, newItem) {
        let arr = props.items.slice();

        if (isBlank(newItem)) {
            arr.splice(idx, 1);
        } else {
            arr.splice(idx, 1, newItem);
        }

        props.handleUpdate(arr);
    }

    function dropItem(idx) {
        let arr = props.items.slice();
        arr.splice(idx, 1);
        props.handleUpdate(arr);
    }

    function AddButton() {
        return(
            <Button
                variant="primary"
                onClick={() => {addItem()}}
            >Add { props.label }</Button>
        );
    }

    return(
        <Form.Group>
            { props.items.map((val, idx) => {
                    return(
                        <EditableListTextItem
                            label={ idx === 0 ? props.label : null }
                            key={val}
                            val={val}
                            handleUpdate={(txt) => {updateItem(idx, txt);}}
                            handleRemove={() => { dropItem(idx);}}
                />)})}
            { props.items.length > 0 && isBlank(props.items.slice(-1)[0])
                ? <></>
                : <Row>
                    <Col sm={3}/>
                    <Col className="text-left" md={{span: 8}}>
                        <AddButton />
                    </Col>
                  </Row>
            }
        </Form.Group>
    );
}

/* Produce an individually editable text item
    props expects
    * label - label text
    * val - initial text value
    * handleUpdate - function should take a replacement text value, update
      parent stat
    * handleRemove - function should remove the item from the parent state
*/

function EditableListTextItem(props) {
    const [text, setText] = useState(props.val);
    const [editing, setEditing] = useState(false);
    const [hovering, setHovering] = useState(false);

    function save() {
        setEditing(false);
        props.handleUpdate(text);
    }

    function handleEnterKey(press) {
        if (editing && press.key === "Enter") {
            save();
        }
    }

    function RemoveButton() {
        return(
            <Button
                variant="danger"
                onClick={ props.handleRemove }
            >X</Button>
        );
    }

    return(
        <Row
            onMouseOver={() => setHovering(true)}
            onMouseOut={() => setHovering(false)}
        >
            <Col sm={3}>
                <Form.Label>
                    { props.label }
                </Form.Label>
            </Col>
            <Col md={{span: 8}}>
            <Form.Control
                onChange={e => { setText(e.target.value)}}
                onFocus={() => setEditing(true)}
                onBlur={() => save()}
                onKeyDown={(e) => {handleEnterKey(e)}}
                value={text}
                readOnly={ !editing }
            />
            </Col>
            <Col md={{span: 1}}>
            { hovering ? <RemoveButton /> : <></> }
            </Col>
        </Row>
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

        * label - string for the option label
        * name - string for the entire selection set
        * value - value of the radio option
        * handleChange - function to set the new value
        * checked - boolean
        */

        let itemId = props.name + props.value;

        return (
            <div>
                <div className="radioContainer">
                    <input type="radio" name={props.name} id={itemId}
                           value={props.value} className="form-check-input"
                           defaultChecked={props.checked}
                           onChange={() => {
                                console.debug("selected " +  props.value);
                                props.handleChange(props.value); }
                           }
                    />
                    <label htmlFor={ itemId } className="form-check-label">{props.label}</label>
                </div>
            </div>
        );
    }

    return(
        <div className="container text-left">
            <div className="row">
                <div className="col">{ props.label }</div>
            </div>

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

        </div>
    );
}


function isBlank(str) {
    return (!str || /^\s*$/.test(str));
}
