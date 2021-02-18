import React, { useState, useReducer } from 'react';
import Petitioner from './components/Petitioner';
import Petition from './components/Petition';
import Dockets from './components/Dockets';
import Charges from './components/Charges';
import Restitution from './components/Restitution';

import "./style.css";
import axios from 'axios';

import { Button, Form } from 'react-bootstrap';

/* TODO:
    - Include ratio.
    - Move components to be imported.
*/

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

export default function GeneratePage(props) {
    /* Props accepts:
        - petitionFields: single petition fields object, as described in the api glossary
    */

    const fieldsFromRouterState = props.location && props.location.state ? props.location.state.petitionFields : null
    let petitionFields = fieldsFromRouterState || props.petitionFields || defaultPetitionFields;

    const [petitioner, setPetitioner] = useReducer(mergeReduce, petitionFields.petitioner);
    const [petition, setPetition] = useReducer(mergeReduce, petitionFields.petition);
    const [dockets, setDockets] = useState(petitionFields.dockets);
    const [charges, setCharges] = useState(petitionFields.charges);
    const [restitution, setRestitution] = useReducer(mergeReduce, petitionFields.restitution);

    function postGeneratorRequest() {
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

    return (
        <Form className="generator">
            <Petitioner {... petitioner} handleChange={setPetitioner} />
            <Petition {... petition} handleChange={setPetition} />
            <Dockets dockets={dockets} handleChange={setDockets} />
            <Charges charges={charges} handleChange={setCharges} />
            <Restitution {... restitution} handleChange={setRestitution} />
            <Button onClick={postGeneratorRequest}>Generate Petition</Button>
        </Form>

    );
}

function today() {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0');
    var yyyy = today.getFullYear();
    return(yyyy + '-' + mm + '-' + dd);
}
