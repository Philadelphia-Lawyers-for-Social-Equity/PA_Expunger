import React, { useEffect, useState, useReducer } from "react";
import { useHistory } from 'react-router-dom';
import { Link } from "react-router-dom";
import Alert from 'react-bootstrap/Alert';
import Petitioner from "./components/Petitioner";
import Petition from "./components/Petition";
import Dockets from "./components/Dockets";
import Charges from "./components/Charges";
import Fines from "./components/Fines";
import Progress from "./components/Progress";
import { useAuth } from "../../context/auth";
import { initialPetitionState, usePetitions } from "../../context/petitions";
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
    docket_info: {
        otn: "",
        judge: "",
        ratio: "full",
    },
    docket_numbers: [],
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
    const history = useHistory();
    const { authTokens } = useAuth();
    const { petitions, setPetitions } = usePetitions();
    const { petitioner, setPetitioner } = usePetitioner();

    const [petitionNumber, setPetitionNumber] = useState(0)

    const fieldsFromRouterState =
        props.location && props.location.state
            ? props.location.state.petitionFields
            : null;
    let petitionFields =
        fieldsFromRouterState || props.petitionFields || defaultPetitionFields;
    const [success, setSuccess] = useState(false);
    const [busy, setBusy] = useState(false);
    const [downloadUrls, setDownloadUrls] = useState({0: ""});
    const [error, setError] = useState("");

    const formDisabled = busy || success[petitionNumber];
    const totalPetitions = petitions.length;
    const multiPetition = (totalPetitions > 1) ? true : false;

    useEffect(() => {
        if (success[petitionNumber] === true) {
            document.getElementById("downloadbutton").scrollIntoView({ behavior: "smooth" });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [success])

    // re-create petitions state from history after page refresh
    useEffect(() => {
        if (petitions === initialPetitionState) {
            setPetitions(props.location.state.petitionFields.petitions)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    function postGeneratorRequest() {
        let petitionFields = {
            petitioner: petitioner,
            petition: { ...petitions[petitionNumber].docket_info, date: today() },
            dockets: petitions[petitionNumber].docket_numbers,
            charges: petitions[petitionNumber].charges,
            fines: petitions[petitionNumber].fines,
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
                    setDownloadUrls({
                        ...downloadUrls,
                        [petitionNumber]: downloadUrl
                    });
                    setSuccess({
                        ...success,
                        [petitionNumber]: true
                    });
                    setError("");
                } else {
                    throw new Error(`${res.status}: ${res.statusText}`)
                }
            })
            .catch((error) => {
                setSuccess({
                    ...success,
                    [petitionNumber]: false
                });
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
        setSuccess({
            ...success,
            [petitionNumber]: false
        });
        setError("");
    }

    function handleSubmit() {
        setError("");
        setSuccess({
            ...success,
            [petitionNumber]: false
        });

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

    function savePetitions() {
        // update history state to include any revisions to petition
        history.replace("/generate", {"petitionFields": {
            petitioner: props.location.state.petitionFields.petitioner,
            petitions: petitions
        }})
    }

    function handlePrevious() {
        setPetitionNumber(n => {
            if (n >= 0) return n - 1
        })
    }
    
    function handleNext() {
        savePetitions();
        if (petitionNumber === totalPetitions - 1) {
            // TODO: navigate to "review petitions" component
        } else setPetitionNumber(n => n + 1);
    }

    const nextButton = (petitionNumber === totalPetitions - 1)
        ? <div className="mr-2 d-inline">
            <Button onClick={handleNext} >
                Review petitions
            </Button>
        </div>
        : <div className="mr-2 d-inline">
            <Button onClick={handleNext} >
                Save & Continue
            </Button>
        </div>

    if (petitions === initialPetitionState) {
        return null
    }

    return (
        <Form className="generator">
            <Petitioner {...petitioner} disabled={formDisabled} />
            <Petition petitionNumber={petitionNumber} disabled={formDisabled} />
            <Dockets petitionNumber={petitionNumber} disabled={formDisabled} />
            <Charges petitionNumber={petitionNumber} disabled={formDisabled} />
            <Fines petitionNumber={petitionNumber} disabled={formDisabled} />
            {error && <Form.Group as={Row}><Col><Alert variant="warning">{error}</Alert></Col></Form.Group>}
            <Form.Group as={Row} className="d-flex justify-content-start">
                <div>
                    {multiPetition && <div className="mr-2 d-inline">
                        <Button onClick={handlePrevious} disabled={petitionNumber === 0}>
                            Previous Petition
                        </Button>
                    </div>}
                    {multiPetition && nextButton}
                    <div className="mr-2 d-inline">
                        <Button onClick={handleSubmit} disabled={formDisabled}>
                            Generate Petition
                        </Button>
                    </div>
                </div>
                <div>
                    <Progress petitionNumber={petitionNumber} totalPetitions={totalPetitions} />
                </div>
            </Form.Group>
            {success[petitionNumber] && (
                <>
                    <Form.Group as={Row}>
                        <Col><Alert variant="success">
                            Your petition has been generated. Please ensure that it is correct!
                        </Alert></Col>
                    </Form.Group>
                    <Form.Group as={Row}>
                        <Col>
                            <div className="mr-2 d-inline" id="downloadbutton">
                                <a className="btn btn-primary" href={downloadUrls[petitionNumber]} download="petition.docx">Download</a>
                            </div>
                            <div className="mr-2 d-inline">
                                <Button onClick={edit}>Edit Petition</Button>
                            </div>
                            {(petitionNumber === totalPetitions - 1) && <div className="mr-2 d-inline">
                                <Link to={{
                                    pathname: '/action',
                                    state: {petitioner: petitioner}
                                    }} ><Button>New Petition</Button></Link>
                            </div>}
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
