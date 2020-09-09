import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, Modal, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';
// thead, tbody, tr, td, th
// import { useAuth } from '../../context/auth';


export default function FileUpload() {

    const history = useHistory();

    const [fileName, setFileName] = useState(undefined);
    const [isError, setIsError] = useState(false);
    const [isError2, setIsError2] = useState(false);
    const [filePassed, setFilePassed] = useState(false);

    const [charges, setCharges] = useState({});
    const [checkedItems, setCheckedItems] = useState({});

    const [fullName, setFullName] = useState("");
    const [aliases, setAliases] = useState("");
    const [dob, setDOB] = useState("");
    const [street1, setStreet1] = useState("");
    const [street2, setStreet2] = useState("");
    const [city, setCity] = useState("");
    const [twoLetterState, setTwoLetterState] = useState("");
    const [zipcode, setZipcode] = useState("");
    const [ssn, setSSN] = useState("");
    const [otn, setOTN] = useState("");
    const [dc, setDC] = useState("");
    const [arrestAgency, setArrestAgency] = useState("");
    const [arrestDate, setArrestDate] = useState("");
    const [arrestOfficer, setArrestOfficer] = useState("");
    const [judge, setJudge] = useState("");
    const [docket, setDocket] = useState("");
    const [restitutionTotal, setRestitutionTotal] = useState(0.0);
    const [restitutionPaid, setRestitutionPaid] = useState(0.0);

    // On click for the cancel button
    function returnLogin() {
        history.push("/login");
    }

    // On change for getting file
    function getFile(files) {
        setFileName(files[0]);
    }

    // On click to store the attorney information to local storage
    function choseFile() {

        console.log(fileName);

        // Need to check if a file is chosen
        if (fileName === undefined) {
            setIsError(true);
        }
        else {
            let pdfdata = new FormData();
            pdfdata.append('name', 'docket_file');
            pdfdata.append('docket_file', fileName);

            // post to generate profile
            const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/parse-docket/";
            const bearer = "Bearer ";
            const token = bearer.concat(localStorage.getItem("access_token"));
            var config = {
                'headers': { 'Authorization': token }
            };

            axios.post(url, pdfdata, config)
                .then(res => {
                    
                    if (res.status === 200) {

                        console.log(res.data);
                        setDocket(res.data.docket);
                        setFullName(res.data.petitioner.name);
                        setCharges(res.data.charges);
                        setAliases(res.data.petitioner.aliases);
                        setDOB(res.data.petitioner.dob);
                        setOTN(res.data.petition.otn);
                        setArrestAgency(res.data.petition.arrest_agency);
                        setArrestDate(res.data.petition.arrest_date);
                        setArrestOfficer(res.data.petition.arrest_officer);
                        setJudge(res.data.petition.judge);

                        //missing DC number, restitution amounts (pending Pablo)

                        setFilePassed(true);
                    }
                })
                .catch(err => {
                    console.log(err);
                });
        }
    }

    // checkboxes onchange for charges table
    function handleCheckbox(target) {
        setCheckedItems({...checkedItems, [target.name] : target.checked});
    }

     // On click to check that the manual entry fields are entered before POST
    function checkInfo() {

    if (street1 === "" || city === "" || twoLetterState === "" || zipcode === "" || ssn === "") {
      setIsError2(true);
    }
    else {
      // Make the Post call
      getDocFile();
    }
  }

  function getDocFile() {

    var newCharges = [];

    for (var i = 0; i < charges.length; i++) {
        if(!document.getElementById(i.toString()).children[0].checked) {
            newCharges.push(charges[i]);
        };
    }

    console.log(newCharges);

    // Current date
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
        "otn": otn,
        "dc": dc,
        "arrest_agency": arrestAgency,
        "arrest_date": arrestDate,
        "arrest_officer": arrestOfficer,
        "judge": judge
      },
      "charges" : newCharges,
      "docket": docket,
      "restitution": {
        "total": parseFloat(restitutionTotal),
        "paid": parseFloat(restitutionPaid)
      }
    }

    console.log(realData);

    // Make an axios POST call to api/v0.2.0/petition/generate/
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
            // return data
            // console.log("Posted");
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
  } //close getDocFile function

    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header>
                    <Modal.Title>Upload File</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Col>
                        <input type="file" name="docket_file" onChange={e => { getFile(e.target.files); }} />
                    </Col>
                </Modal.Body>

                <Modal.Footer>
                    <Button id="returnToLoginButton" onClick={returnLogin}>Cancel</Button>
                    <Button id="fileButton" onClick={choseFile}>Submit</Button>
                    {isError && <div>Please select a file</div>}
                </Modal.Footer>
            </Modal.Dialog>


            {filePassed && <div>

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

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Docket Number
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="Docket Number" value={docket} onChange={e => {
                                        setDocket(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

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

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Aliases
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 8 }}>
                                    <Form.Control placeholder="Aliases (comma-separated)" value={aliases} onChange={e => {
                                        setAliases(e.target.value);
                                    }} />
                                </Col>
                            </Form.Group>

                            <Form.Group as={Row}>
                                <Col sm={3}>
                                    <Form.Label>
                                        Date of Birth
                                </Form.Label>
                                </Col>
                                <Col md={{ span: 3 }}>
                                    <Form.Control placeholder="yyyy-mm-dd" value={dob} onChange={e => {
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
                                    <Form.Control placeholder="########" onChange={e => {
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
                                    <Form.Control placeholder="yyyy-mm-dd" value={arrestDate} onChange={e => {
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
                                    <Form.Control placeholder="Total" id="totalRestitution" onChange={e => {
                                        setRestitutionTotal(e.target.value);
                                    }} />
                                </Col>
                                <Col sm={4}>
                                    <Form.Control placeholder="Paid" id="paidRestitution" onChange={e => {
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
                    </Form>

                    </Col>

                </Row>

                </div>}

        </div >
    );
}
