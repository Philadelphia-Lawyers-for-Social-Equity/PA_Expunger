import React, { useState, useReducer } from "react";
import Petitioner from "./components/Petitioner";
import Petition from "./components/Petition";
import Dockets from "./components/Dockets";
import Charges from "./components/Charges";
import Fines from "./components/Fines";
import { useAuth } from "../../context/auth";

import "./style.css";
import axios from "axios";

import { Button, Form } from "react-bootstrap";

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
        petitionFields.petition
    );
    const [dockets, setDockets] = useState(petitionFields.dockets);
    const [charges, setCharges] = useState(petitionFields.charges);
    const [fines, setFines] = useReducer(mergeReduce, petitionFields.fines);
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
        axios
            .post(url, petitionFields, postRequestConfig())
            .then((res) => {
                if (res.status === 200) {
                    let blob = new Blob([res.data], {
                        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    });
                    let downloadUrl = window.URL.createObjectURL(blob);
                    let filename = "petition.docx";
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
            })
            .catch((error) => {
                console.error(error);
            });
    }

    function successfulSubmit() {
        alert("Your petition has been successfully generated.");
    }

    function handleSubmit() {
        setError("");

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
            successfulSubmit();
        }
    }

    function ErrorSection({ error }) {
        return <p className="invalid-warning">{error}</p>;
    }

    return (
        <Form className="generator">
            <Petitioner {...petitioner} handleChange={setPetitioner} />
            <Petition {...petition} handleChange={setPetition} />
            <Dockets dockets={dockets} handleChange={setDockets} />
            <Charges charges={charges} handleChange={setCharges} />
            <Fines {...fines} handleChange={setFines} />
            {error && <ErrorSection error={error} />}
            <Button onClick={handleSubmit} className="generate-button">
                Generate Petition
            </Button>
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
