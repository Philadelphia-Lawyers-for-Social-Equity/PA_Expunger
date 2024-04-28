import React, { useState, useReducer } from "react";
import Alert from 'react-bootstrap/Alert';
import Petitioner from "./components/Petitioner";
import Petition from "./components/Petition";
import Dockets from "./components/Dockets";
import Charges from "./components/Charges";
import { validateSubmission } from './helpers/validatorUtils';
import Fines from "./components/Fines";
import { useAuth } from "../../context/auth";

import "./style.css";
import axios from "axios";

import { Button, Form, Row, Col } from "react-bootstrap";

/* TODO:
    - Include ratio.
    - Move components to be imported.
*/

const url =
    process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/generate/";
const defaultPetitionFields = {
    petitioner: {
        name: "",
        aliases: [],
        dob: "",
        ssn: "",
        address: {
            street1: "",
            street2: "",
            city: "",
            state: "",
            zipcode: "",
        },
    },
    petition: {
        otn: "",
        judge: "",
        ratio: "full",
    },
    dockets: [],
    charges: [],
    fines: {
        total: 0,
        paid: 0,
    },
};

function mergeReduce(initial, changes) {
    return { ...initial, ...changes };
}

export default function GeneratePage(props) {
    /* Props accepts:
        - petitionFields: single petition fields object, as described in the api glossary
    */
    const { authTokens } = useAuth();

    const [petitionNumber, setPetitionNumber] = useState(0)

    const fieldsFromRouterState =
        props.location && props.location.state
            ? props.location.state.petitionFields
            : null;
    let petitionFields =
        fieldsFromRouterState || props.petitionFields || defaultPetitionFields;

    const [petitioner, setPetitioner] = useReducer(
        mergeReduce,
        petitionFields.petitioner
    );
    const [petition, setPetition] = useReducer(
        mergeReduce,
        petitionFields.petitions[petitionNumber].docket_info
    );
    const [dockets, setDockets] = useState(petitionFields.petitions[petitionNumber].docket_numbers);
    const [charges, setCharges] = useState(petitionFields.petitions[petitionNumber].charges);
    const [fines, setFines] = useReducer(mergeReduce, petitionFields.petitions[petitionNumber].fines);
    const [success, setSuccess] = useState(false);
    const [busy, setBusy] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState("");
    const [errors, setErrors] = useState(null);
    const [serviceError, setServiceError] = useState(null);

    function postGeneratorRequest() {
        let petitionFields = {
            petitioner: petitioner,
            petition: { ...petition, date: today() },
            dockets: dockets,
            charges: charges,
            fines: fines,
        };

        if (!petitionFields.petition.ratio) {
            petitionFields.petition.ratio = "full";
        }

        function postRequestConfig() {
            const token = `Bearer ${authTokens.access}`;
            return {
                responseType: "arraybuffer",
                headers: { Authorization: token },
            };
        }

        console.info(petitionFields);
        setBusy(true);
        axios
            .post(url, petitionFields, postRequestConfig())
            .then((res) => {
                if (res.status === 200) {
                    let blob = new Blob([res.data], {
                        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    });
                    let downloadUrl = window.URL.createObjectURL(blob);
                    setDownloadUrl(downloadUrl);
                    setSuccess(true);
                    setServiceError(null);
                    setTimeout(() => {
                        // needs to happen after DOM updates
                        document.getElementById("downloadbutton").scrollIntoView({ behavior: "smooth" });
                    });
                } else {
                    throw new Error(`${res.status}: ${res.statusText}`)
                }
            })
            .catch((error) => {
                setSuccess(false);
                setServiceError("There was an error generating the petition.");
                console.error(error);
            })
            .finally(() => {
                setBusy(false);
            });
    }

    function edit() {
        setSuccess(false);
        setErrors(null);
    }

    function handleSubmit() {
        setErrors(null);
        /**
         * Let's build an array of errors per section.
         * 
         * The validateSubmissions utility function will return:
         *  A.  an empty array if the section's inputs are valid
         *              OR
         *  B.  an array of the following structure:
         *      [ { sectionName: [ array of invalid input descriptions ] }]
         *      Example: [ { petitioner: ['date of birth', 'Social Security number'] } ]
         *      
         *      NOTE: The invalid input descriptions are displayed to the user which is why
         *      using the object's key (dob, ssn) was decided against.
         */
        const tempErrors = [
            ...validateSubmission('petitioner', petitioner),
            ...validateSubmission('petition', petition),
            ...validateSubmission('dockets', dockets),
            ...validateSubmission('charges', charges),
            ...validateSubmission('fines', fines),
        ];
        if (tempErrors.length) {
            setErrors(tempErrors)
        } else {
            postGeneratorRequest();
        }
    }

  function ErrorSection({errors}) {
    return (
      <div className="invalid-warning">
        <h5>Please correct the following missing or invalid inputs:</h5>
        {errors && errors.map(error => {
          const key = Object.keys(error);
          const sectionHeading = key[0][0].toUpperCase() + key[0].slice(1);
          return (
            <div key={key} className='invalid-input-section'>
              {sectionHeading}
              <ul>
                {error[key].map(invalidEntry => <li key={invalidEntry}>{invalidEntry}</li>)}
              </ul>
            </div>
          )
        })}
      </div>
    );
  }

    const formDisabled = busy || success;

    return (
        <Form className="generator">
            <Petitioner {...petitioner} handleChange={setPetitioner} disabled={formDisabled} />
            <Petition {...petition} handleChange={setPetition} disabled={formDisabled} />
            <Dockets dockets={dockets} handleChange={setDockets} disabled={formDisabled} />
            <Charges charges={charges} handleChange={setCharges} disabled={formDisabled} />
            <Fines {...fines} handleChange={setFines} disabled={formDisabled} />
            {serviceError && <Form.Group as={Row}><Col><Alert variant="warning">{serviceError}</Alert></Col></Form.Group>}
            {errors && <ErrorSection errors={errors} />}
            <Form.Group as={Row}>
                <Col>
                    <Button onClick={handleSubmit} disabled={formDisabled}>
                        Generate Petition
                    </Button>
                </Col>
            </Form.Group>
            {success && (
                <>
                    <Form.Group as={Row}>
                        <Col><Alert variant="success">
                            Your petition has been generated. Please ensure that it is correct!
                        </Alert></Col>
                    </Form.Group>
                    <Form.Group as={Row}>
                        <Col>
                            <div class="mr-2 d-inline" id="downloadbutton">
                                <a class="btn btn-primary" href={downloadUrl} download="petition.docx">Download</a>
                            </div>
                            <div class="mr-2 d-inline">
                                <Button onClick={edit}>Edit Petition</Button>
                            </div>
                            <div class="mr-2 d-inline">
                                <Button href="/action">New Petition</Button>
                            </div>
                        </Col>
                    </Form.Group>
                </>
            )}
        </Form>
    );
}

function today() {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, "0");
    var mm = String(today.getMonth() + 1).padStart(2, "0");
    var yyyy = today.getFullYear();
    return yyyy + "-" + mm + "-" + dd;
}
