import React, { useEffect, useState, useReducer } from "react";
import { Link } from "react-router-dom";
import Alert from 'react-bootstrap/Alert';
import Petitioner from "./components/Petitioner";
import Petition from "./components/Petition";
import Dockets from "./components/Dockets";
import Charges from "./components/Charges";
import Fines from "./components/Fines";
import { useAuth } from "../../context/auth";
import { usePetitioner, initialPetitionerState } from "../../context/petitioner";

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
    const { petitioner, setPetitioner } = usePetitioner();

    const [petitionNumber, setPetitionNumber] = useState(0)

    const fieldsFromRouterState =
        props.location && props.location.state
            ? props.location.state.petitionFields
            : null;
    let petitionFields =
        fieldsFromRouterState || props.petitionFields || defaultPetitionFields;

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
    const [error, setError] = useState("");

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
                    setError("");
                    setTimeout(() => {
                        // needs to happen after DOM updates
                        document.getElementById("downloadbutton").scrollIntoView({ behavior: "smooth" });
                    });

                    //history.push("/generate");
                } else {
                    throw new Error(`${res.status}: ${res.statusText}`)
                }
            })
            .catch((error) => {
                setSuccess(false);
                setError("There was an error generating the petition.");
                console.error(error);
            })
            .finally(() => {
                setBusy(false);
            });
    }

    // re-create petitioner state from history after page refresh
    useEffect(() => {
        if (petitioner === initialPetitionerState) {
            setPetitioner(props.location.state.petitionFields.petitioner);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])
    

    function edit() {
        setSuccess(false);
        setError("");
    }

    function handleSubmit() {
        setError("");
        setSuccess(false);

        const ssn = petitioner.ssn;
        const hasDashes = /(-)/.test(ssn);

        if (!petitioner.name) {
            setError("Please enter a name.");
        } else if (!petitioner.dob) {
            setError("Please enter a valid birth date.");
        } else if (!ssn) {
            setError("Please enter a valid Social Security number.");
        } else if (
            (hasDashes && ssn.length !== 11) ||
            (!hasDashes && ssn.length !== 9)
        ) {
            setError("Please enter a valid Social Security number.");
        } else if (
            !petitioner.address ||
            !petitioner.address.street1 ||
            !petitioner.address.city ||
            !petitioner.address.state ||
            !petitioner.address.zipcode
        ) {
            setError("Please enter a valid address.");
        } else {
            postGeneratorRequest();
        }
    }

    const formDisabled = busy || success;

    return (
        <Form className="generator">
            <Petitioner {...petitioner} disabled={formDisabled} />
            <Petition {...petition} handleChange={setPetition} disabled={formDisabled} />
            <Dockets dockets={dockets} handleChange={setDockets} disabled={formDisabled} />
            <Charges charges={charges} handleChange={setCharges} disabled={formDisabled} />
            <Fines {...fines} handleChange={setFines} disabled={formDisabled} />
            {error && <Form.Group as={Row}><Col><Alert variant="warning">{error}</Alert></Col></Form.Group>}
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
                                <Link to={{
                                    pathname: '/action',
                                    state: {petitioner: petitioner}
                                    }} ><Button>New Petition</Button></Link>
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
