import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, Modal, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';
// import { useAuth } from '../../context/auth';


export default function SearchPage() {

    const history = useHistory();
    const [searchFirstName, setSearchFirstName] = useState("");
    const [searchLastName, setSearchLastName] = useState("");

    // const [dob, setDOB] = useState("");

    const [isError, setIsError] = useState(false);

    const [docketData, setDocketData] = useState([]);

    // const [docketDataDisplay, setDocketDataDisplay] = useState(false);

    // const [CountyName, setCountyName] = useState("");
    // const [DocketNumber, setDocketNumber] = useState("");
    // const [FiledDate, setFiledDate] = useState("");
    // const [LastName, setLastName] = useState("");
    // const [FirstName, setFirstName] = useState("");
    // const [MiddleName, setMiddleName] = useState("");
    // const [City, setCity] = useState("");
    // const [State, setState] = useState("");
    // const [ZipCode, setZipCode] = useState("");
    // const [OffenseTrackingNumber, setOffenseTrackingNumber] = useState("");
    // const [GenderCode, setGenderCode] = useState("");
    // const [RaceCode, setRaceCode] = useState("");
    // const [BirthDate, setBirthDate] = useState("");
    // const [OriginatingOffenseSequence, setOriginatingOffenseSequence] = useState("");
    // const [StatuteType, setStatuteType] = useState("");
    // const [StatuteTitle, setStatuteTitle] = useState("");
    // const [StatuteSection, setStatuteSection] = useState("");
    // const [StatuteSubSection, setStatuteSubSection] = useState("");
    // const [InchoateStatuteTitle, setInchoateStatuteTitle] = useState("");
    // const [InchoateStatuteSection, setInchoateStatuteSection] = useState("");
    // const [InchoateStatuteSubSection, setInchoateStatuteSubSection] = useState("");
    // const [OffenseDisposition, setOffenseDisposition] = useState("");
    // const [OffenseDate, setOffenseDate] = useState("");
    // const [OffenseDispositionDate, setOffenseDispositionDate] = useState("");
    // const [OffenseDescription, setOffenseDescription] = useState("");
    // const [CaseDisposition, setCaseDisposition] = useState("");
    // const [CaseDispositionDate, setCaseDispositionDate] = useState("");
    // const [OffenseGrade, setOffenseGrade] = useState("");
    // const [DisposingJudge, setDisposingJudge] = useState("");



    // const [dockets, setDockets] = useState([]);
    // const [aliases, setAliases] = useState([]);
    // const [street1, setStreet1] = useState("");
    // const [street2, setStreet2] = useState("");
    // const [city, setCity] = useState("");
    // const [twoLetterState, setTwoLetterState] = useState("");
    // const [zipcode, setZipcode] = useState("");
    // const [ssn, setSSN] = useState("");
    // const [otn, setOTN] = useState("");
    // const [dc, setDC] = useState("");
    // const [arrestAgency, setArrestAgency] = useState("");
    // const [arrestDate, setArrestDate] = useState("");
    // const [arrestOfficer, setArrestOfficer] = useState("");
    // const [judge, setJudge] = useState("");
    // const [restitutionTotal, setRestitutionTotal] = useState(0.0);
    // const [restitutionPaid, setRestitutionPaid] = useState(0.0);


    // On click for the cancel button
    function returnToLogin() {
        history.push("/login");
    }

    // GET for docket info from database
    function getData() {

        // Need to check if inputs are available
        if (searchFirstName === "" || searchLastName === "") {
            setIsError(true);
        }
        else {
            setIsError(false);
            console.log("fullname is " + searchFirstName + " " + searchLastName);

            // get database
            const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/dockets/?firstName=" + searchFirstName + '&lastName=' + searchLastName;
            console.log("url is " + url);
            const bearer = "Bearer ";
            const token = bearer.concat(localStorage.getItem("access_token"));
            var config = {
                'headers': { 'Authorization': token }
            };

            axios.get(url, config)
                .then(res => {
                    if (res.status === 200) {
                        console.log(res.data);

                        setDocketData(res.data);

                        // setCountyName(res.data.county_name);
                        // setDocketNumber(res.data.docket_number);
                        // setFiledDate(res.data.filed_date);
                        // setLastName(res.data.last_name);
                        // setFirstName(res.data.first_name);
                        // setMiddleName(res.data.middle_name);
                        // setCity(res.data.city);
                        // setState(res.data.state);
                        // setZipCode(res.data.zipcode);
                        // setOffenseTrackingNumber(res.data.offense_tracking_number);
                        // setGenderCode(res.data.gender_code);
                        // setRaceCode(res.data.race_code);
                        // setBirthDate(res.data.birth_date);
                        // setOriginatingOffenseSequence(res.data.originating_offense_sequence);
                        // setStatuteType(res.data.statute_type);
                        // setStatuteTitle(res.data.statute_title);
                        // setStatuteSection(res.data.statute_section);
                        // setStatuteSubSection(res.data.statute_sub_section);
                        // setInchoateStatuteTitle(res.data.inchoate_statute_title);
                        // setInchoateStatuteSection(res.data.inchoate_statute_section);
                        // setInchoateStatuteSubSection(res.data.inchoate_statute_sub_section);
                        // setOffenseDisposition(res.data.offense_disposition);
                        // setOffenseDate(res.data.offense_date);
                        // setOffenseDispositionDate(res.data.offense_disposition_date);
                        // setOffenseDescription(res.data.offense_description);
                        // setCaseDisposition(res.data.case_disposition);
                        // setCaseDispositionDate(res.data.case_disposition_date);
                        // setOffenseGrade(res.data.offense_grade);
                        // setDisposingJudge(res.data.disposing_judge);

                        // if (JSON.stringify(res.data.restitution)!=JSON.stringify({})) {
                        //     setRestitutionTotal(res.data.restitution.total.toFixed(2));
                        //     setRestitutionPaid(res.data.restitution.paid.toFixed(2));
                        // }

                        //setDocketDataDisplay(true);
                    }
                })
                .catch(err => {
                    console.log(err);
                });
        }
    }


    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header>
                    <Modal.Title>Search by Name</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Col>
                        First Name: <input name="search_first_name" onChange={e => { setSearchFirstName(e.target.value); }} />
                    </Col>
                    <Col>
                        Last Name: <input name="search_last_name" onChange={e => { setSearchLastName(e.target.value); }} />
                    </Col>
                </Modal.Body>

                <Modal.Footer>
                    <Button id="returnToLoginButton" onClick={returnToLogin}>Cancel</Button>
                    <Button id="submitNameButton" onClick={getData}> Submit</Button>
                    {isError && <div>Please fill in search terms</div>}
                </Modal.Footer>
            </Modal.Dialog>


            <Row style={{ margin: `80px` }}>
                <Col md={{ span: 8, offset: 2 }}>
                    returned data here
                    {docketData.map(docket => (<Button id="attorneyNames" key={docket.docket_number} onClick={e => {

                    }}>{docket.docket_number}</Button>))}
                </Col>
            </Row>

        </div >
    );
}

