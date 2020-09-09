import React, { useState, useEffect } from 'react';
import { Redirect } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, ButtonGroup, Modal, Col } from 'react-bootstrap';
// import { useAuth } from '../../context/auth';


export default function LandingPage() {
    const [attorneyData, setAttorneyData] = useState([]);
    const [attorneyKey, setAttorneyKey] = useState(0);
    const [attorneyName, setAttorneyName] = useState("");
    const [attorneyBar, setAttorneyBar] = useState("");
    const [attorneyURL, setAttorneyURL] = useState("");
    const [isAttorneyChosen, setAttorneyChosen] = useState(false);
    const [profileGenerated, setProfileGenerated] = useState(false);
    const [isError, setIsError] = useState(false);

    // useEffect is the React Hook equivalent to ComponentDidMount
    useEffect(() => {

        const bearer = "Bearer ";
        const token = bearer.concat(localStorage.getItem("access_token"));
        var config = {
            'headers': { 'Authorization': token }
        };

        // Get to return all attorneys (PKs are integers)
        const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/attorneys/";
        axios.get(url, config)
            .then(
                res => {
                    if (res.status === 200) {
                        // return data
                        setAttorneyData(res.data);
                    }
                }
            )
    }, []); // empty array as the second argument will limit to one get call


    // On click for the cancel button
    function returnLogin() {
        return <Redirect to="/login" />;
    }

    // On click to store the attorney information to local storage
    function choseAttorney() {

        // No attorney chosen if blank
        if (attorneyKey === "") {
            setIsError(true);
        }
        else {
            setAttorneyChosen(true);
        }
    }

    if (isAttorneyChosen) {

        const profiledata = {
            "attorney" : attorneyKey,
            "organization" : 1,
            "user" : {
                "first_name" : localStorage.getItem("firstName"),
                "last_name" : localStorage.getItem("lastName"),
                "email" : localStorage.getItem("email"),
                "username" : localStorage.getItem("username")            
            }
        };

        // post to generate profile
        const profileurl = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/my-profile/";
        const bearer = "Bearer ";
        const token = bearer.concat(localStorage.getItem("access_token"));
        var config = {
            'headers': { 'Authorization': token }
        };

        axios.post(profileurl, profiledata, config)
            .then(res => {
                if (res.status === 201) {
                    setProfileGenerated(true);
                }
            })
            .catch(err => { 
                console.log(err); 
            });
    }

    if (profileGenerated) {
        // redirect to input form
        return <Redirect to="/inputform" />;
    }

    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header closeButton>
                    <Modal.Title>Attorneys</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Col>
                        Please select the attorney that you will be filing for:
                        <ButtonGroup vertical >
                            {attorneyData.map(item => (<Button id="attorneyNames" key={item.pk} onClick={e => {
                                setAttorneyKey(item.pk);
                                setAttorneyName(item.name);
                                setAttorneyBar(item.bar);
                                setAttorneyURL(item.url);
                            }}>{item.name}</Button>))}
                        </ButtonGroup>
                    </Col>
                </Modal.Body>

                <Modal.Footer>
                    <Button id="cancelButton" onClick={returnLogin}>Cancel</Button>
                    <Button id="attorneyNames" onClick={choseAttorney}>Select</Button>
                    {isError && <div>Please select an attorney</div>}
                </Modal.Footer>
            </Modal.Dialog>
        </div>
    );
}
