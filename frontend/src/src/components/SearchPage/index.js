import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, ButtonGroup, Modal, Col, Form, Row, Table, ToggleButton } from 'react-bootstrap';
// import { useAuth } from '../../context/auth';


export default function SearchPage() {

    const history = useHistory();
    const [searchFirstName, setSearchFirstName] = useState("");
    const [searchLastName, setSearchLastName] = useState("");

    // const [dob, setDOB] = useState("");

    const [isError, setIsError] = useState(false);

    const [searchPassed, setSearchPassed] = useState(false);

    const [archiveData, setArchiveData] = useState([]);
    const [checkedItems, setCheckedItems] = useState({});

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
    function getArchiveData() {

        // Need to check if inputs are available
        if (searchFirstName === "" || searchLastName === "") {
            setIsError(true);
        }
        else {
            setIsError(false);
            console.log("fullname is " + searchFirstName + " " + searchLastName);

            // get database
            const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.1/pa_court_archive/search/?firstName=" + searchFirstName + "&lastName=" + searchLastName;
            console.log("url is " + url);
            const bearer = "Bearer ";
            const token = bearer.concat(localStorage.getItem("access_token"));
            var config = {
                'headers': { 'Authorization': token }
            };

            // Enter mock data until api endpoint is ready
            var mockData = [
                {"docket_number" : "MC-51-CR-1234567-2000", "first_name" : "John", "middle_name" : "", "last_name" : "Smith", "birth_date" : "1580-01-06", "filed_date" : "2000-10-23"}, 
                {"docket_number" : "MC-51-CR-7654321-1998", "first_name" : "John", "middle_name" : "Richard", "last_name" : "Smith", "birth_date" : "1980-02-02", "filed_date" : "1998-11-23"}];
            setArchiveData(mockData);

            setSearchPassed(true);
            //Uncomment when api endpoint is ready:
            // axios.get(url, config)
            //     .then(res => {
            //         if (res.status === 200) {
            //             console.log(res.data);

                        //setArchiveData(res.data);

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
                //     }
                // })
                // .catch(err => {
                //     console.log(err);
                // });


        }
    }

    // checkboxes onchange for charges table
    function handleCheckbox(target) {
        setCheckedItems({ ...checkedItems, [target.name]: target.checked });
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
                    <Button id="submitNameButton" onClick={getArchiveData}>Search</Button>
                    {isError && <div>Please fill in search terms</div>}
                </Modal.Footer>
            </Modal.Dialog>

            {searchPassed && <div>
                <Row>
                    <Col>
                        <Table>
                            <thead>
                                <tr>
                                    <th>First</th>
                                    <th>Middle</th>
                                    <th>Last</th>
                                    <th>DOB</th>
                                    <th>Docket Number</th>
                                    <th>Filed Date</th>
                                    <th>Select Docket to generate Petition</th>
                                </tr>
                            </thead>
                            <tbody>
                                {archiveData.map((archivecharge, index) => (<tr key={index}>
                                    <td className="first_name">{archivecharge.first_name}</td>
                                    <td className="middle_name">{archivecharge.middle_name}</td>
                                    <td className="last_name">{archivecharge.last_name}</td>
                                    <td className="birth_date">{archivecharge.birth_date}</td>
                                    <td className="docket_number">{archivecharge.docket_number}</td>
                                    <td className="filed_date">{archivecharge.filed_date}</td>
                                    <td><ToggleButton type="checkbox" variant="dark" id={index} value={index} name={index} checked={checkedItems[index]} onChange={e => { handleCheckbox(e.target); }} /></td>
                                </tr>))}
                            </tbody>
                        </Table>
                    </Col>
                </Row>
            </div> }

        </div >
    );
}

