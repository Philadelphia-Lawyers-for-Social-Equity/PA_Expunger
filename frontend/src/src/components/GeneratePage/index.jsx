import React, { useEffect, useState, useRef } from "react";
import { useHistory } from 'react-router-dom';
import { Alert, Button, Col, Form, Row } from 'react-bootstrap';
import Petitioner from "./components/Petitioner";
import Petition from "./components/Petition";
import Dockets from "./components/Dockets";
import Charges from "./components/Charges";
import Fines from "./components/Fines";
import Progress from "./components/Progress";
import FallbackMessage from "../FallbackMessage";
import { useAuth } from "../../context/auth";
import { useUser } from '../../context/user';
import { initialPetitionState, usePetitions } from "../../context/petitions";
import { usePetitioner, initialPetitionerState } from "../../context/petitioner";
import { useNavBlock } from "../../context/navBlockContext.jsx";
import NavBlock from "../util/navBlock";
import { useIsMounted } from "../../hooks/useIsMounted";

import "./style.css";
import api from "../../services/api";

/* TODO:
    - Include ratio.
    - Move components to be imported.
*/

export default function GeneratePage(props) {
    /* Props accepts:
        - petitionFields: single petition fields object, as described in the api glossary
    */
    const history = useHistory();
    const { authenticatedRequest } = useAuth();
    const { user } = useUser();
    const { petitioner, setPetitioner } = usePetitioner();
    const { petitions, setPetitions, petitionNumber, setPetitionNumber } = usePetitions();
    const { blockNavRef, setBlockNav } = useNavBlock();
    const getIsMounted = useIsMounted();

    const [success, setSuccess] = useState(false);
    const [busy, setBusy] = useState(false);
    const [downloadUrls, setDownloadUrls] = useState({0: ""});
    const [error, setError] = useState("");

    const formDisabled = busy || success[petitionNumber];
    const totalPetitions = petitions.length;
    const multiPetition = (totalPetitions > 1);

    useEffect(() => {
        if (success[petitionNumber] === true) {
            document.getElementById("downloadbutton").scrollIntoView({ behavior: "smooth" });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [success])

    // re-create petitions state from history after page refresh
    useEffect(() => {
        if (props.location.state && props.location.state.petitionFields) {
            if (petitions === initialPetitionState && props.location.state.petitionFields.petitions) {
                setPetitions(props.location.state.petitionFields.petitions);
            }
            if (petitioner === initialPetitionerState && props.location.state.petitionFields.petitioner) {
                setPetitioner(props.location.state.petitionFields.petitioner);
            }
        } else {
            history.push("/");
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
        // When this component mounts, turn on nav block
        setBlockNav(true);

        // cleanup on unmount
        return () => {
            setBlockNav(false);
        };
    }, [setBlockNav]);


    async function postGeneratorRequest() {
        let petitionFields = {
            petitioner: petitioner,
            petition: { ...petitions[petitionNumber].docket_info, date: today() },
            dockets: petitions[petitionNumber].docket_numbers,
            charges: petitions[petitionNumber].charges,
            fines: petitions[petitionNumber].fines,
            organization: user.organization,
            attorney: user.attorney,
        };

        if (!petitionFields.petition.ratio) {
            petitionFields.petition.ratio = "full";
        }

        console.info(petitionFields);
        setBusy(true);
        try {
            let blob = await authenticatedRequest(() => api.generatePetitionBlob(petitionFields));
            let downloadUrl = window.URL.createObjectURL(blob);
            if (getIsMounted()) {
                setDownloadUrls({
                    ...downloadUrls,
                    [petitionNumber]: downloadUrl
                });
                setSuccess({
                    ...success,
                    [petitionNumber]: true
                });
                setError("");
            }
        } catch (error) {
            if (getIsMounted()) {
                setSuccess({
                    ...success,
                    [petitionNumber]: false
                });
                let displayError = "There was an error generating the petition.";
                // The response body is at `error.response.data`, not
                // `error.response`. Reading the latter always yielded
                // undefined, so this fell back to the generic message every
                // time and no backend message ever reached the screen.
                if (error.response?.data?.detail) {
                    displayError = error.response.data.detail;
                }
                setError(displayError);

            }

        } finally {
            if (getIsMounted()) {
                setBusy(false);
            }
        }
    }

    function edit() {
        setSuccess({
            ...success,
            [petitionNumber]: false
        });
        setError("");
    }

    async function handleSubmit() {
        setError("");
        setSuccess({
            ...success,
            [petitionNumber]: false
        });

        if (!isFormValid()) {
            setErrorMessage()
        } else {
            await postGeneratorRequest();
        }
    }

    function isFormValid() {
        return petitioner.name &&
            petitioner.dob &&
            isValidSsn(petitioner.ssn) &&
            petitioner.address &&
            petitioner.address.street1 &&
            petitioner.address.city &&
            petitioner.address.state &&
            petitioner.address.zipcode
    }

    function isValidSsn(ssn) {
        if (!ssn) return false
        const hasDashes = /(-)/.test(ssn);
        const isValidSsn = (hasDashes && ssn.length === 11) ||
            (!hasDashes && ssn.length === 9)
        return isValidSsn
    }

    function setErrorMessage() {
        if (!petitioner.name) {
            setError("Please enter a name.");
        } else if (!petitioner.dob) {
            setError("Please enter a valid birth date.");
        } else if (!isValidSsn(petitioner.ssn)) {
            setError("Please enter a valid Social Security number.");
        } else if (
            !petitioner.address ||
            !petitioner.address.street1 ||
            !petitioner.address.city ||
            !petitioner.address.state ||
            !petitioner.address.zipcode
        ) {
            setError("Please enter a valid address.");
        }
    }

    function savePetitions() {
        // update history state to include any revisions to petition
        history.replace("/generate", {"petitionFields": {
            petitioner,
            petitions
        }})
    }

    function handlePrevious() {
        setPetitionNumber(n => {
            if (n >= 0) return n - 1
        })
    }

    function handleNext() {
        if (!isFormValid()) {
            setErrorMessage()
        } else {
            savePetitions();
            setError("");
            if (petitionNumber === totalPetitions - 1) {
                // TODO: Should this info be saved to page history? delete if not

                // because "/review" is in the list of safe paths, we don't have to change the navBlock ref
                history.push("/review", {
                    "petitionFields": {
                        petitioner,
                        petitions
                    }
                })
            } else setPetitionNumber(n => n + 1);
        }
    }

    const nextButton = (petitionNumber === totalPetitions - 1)
        ?
        <Button onClick={handleNext}>
            Review petitions
        </Button>
        :
        <Button onClick={handleNext}>
            Save & Continue
        </Button>

    if (petitions === initialPetitionState || petitioner === initialPetitionerState
        || typeof petitions[petitionNumber] === 'undefined') {
        return (<FallbackMessage/>);
    }

    function startNewPetition() {
        setBlockNav(false);
        setPetitions(initialPetitionState);
        history.push("/");
    }

    return (
        <Form className="generator">
            <NavBlock blockNav={blockNavRef} />
            <Petitioner {...petitioner} disabled={formDisabled} />
            <Petition petitionNumber={petitionNumber} disabled={formDisabled} />
            <Dockets petitionNumber={petitionNumber} disabled={formDisabled} />
            <Charges petitionNumber={petitionNumber} disabled={formDisabled} />
            <Fines petitionNumber={petitionNumber} disabled={formDisabled} />
            {error && <Form.Group as={Row}><Col><Alert variant="warning">{error}</Alert></Col></Form.Group>}
            <Form.Group as={Row} className="align-items-center mb-3 gx-2" xs="auto">
                {multiPetition && <Col>
                    <Button onClick={handlePrevious} disabled={petitionNumber === 0}>
                        Previous Petition
                    </Button>
                </Col>}
                {multiPetition && <Col>
                    {nextButton}
                </Col>}
                {!multiPetition && <Col>
                    <Button onClick={handleSubmit} disabled={formDisabled}>
                        Generate Petition
                    </Button>
                </Col>}
                <Col>
                    <Progress petitionNumber={petitionNumber} totalPetitions={totalPetitions}/>
                </Col>
            </Form.Group>
            {success[petitionNumber] && (
                <>
                    <Form.Group as={Row}>
                        <Col><Alert variant="success">
                            Your petition has been generated. Please ensure that it is correct!
                        </Alert></Col>
                    </Form.Group>
                    <Form.Group as={Row} className="align-items-center mb-3 gx-2" xs="auto">
                        <Col>
                            <div id="downloadbutton">
                                <a className="btn btn-primary"
                                   href={downloadUrls[petitionNumber]}
                                   download="petition.docx">
                                    Download
                                </a>
                            </div>
                        </Col>
                        <Col>
                            <Button onClick={edit}>Edit Petition</Button>
                        </Col>
                        {(petitionNumber === totalPetitions - 1) && <Col>
                            <Button onClick={startNewPetition}>New Petition</Button>
                        </Col>}
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
