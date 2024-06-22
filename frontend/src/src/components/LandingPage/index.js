import React, { useState, useEffect, useRef } from 'react';
import { Redirect } from 'react-router-dom';
import { Button, Modal } from 'react-bootstrap';
import Form from 'react-bootstrap/Form';
import { useAuth } from "../../context/auth";
import { useUser } from '../../context/user';

export default function LandingPage() {
    const [attorneyData, setAttorneyData] = useState([]);
    const [attorneyKey, setAttorneyKey] = useState(0);
    const [isAttorneyChosen, setAttorneyChosen] = useState(false);
    const [profileGenerated, setProfileGenerated] = useState(false);
    const [isError, setIsError] = useState(false);
    const { authedAxios } = useAuth();
    const { user } = useUser();
    const isMounted = useRef(true);

    // useEffect is the React Hook equivalent to ComponentDidMount
    useEffect(() => {
        if (isMounted.current) {
          isMounted.current = false;
          // Get to return all attorneys (PKs are integers)
          const url = '/expunger/attorneys/';
          authedAxios.get(url)
            .then(
              res => {
                if (res.status === 200) {
                    // return data
                    setAttorneyData(res.data);
                }
              }
            );
        }
   }); // empty array as the second argument will limit to one get call

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
                "first_name" : user.firstName,
                "last_name" : user.lastName,
                "email" : user.email,
                "username" : user.username            
            }
        };

        // post to generate profile
        const profileurl = "/expunger/my-profile/";

        authedAxios.put(profileurl, profiledata)
            .then(res => {
                if (res.status === 200) {
                    setProfileGenerated(true);
                }
            })
            .catch(err => { 
                console.log(err); 
            });
    }

    if (profileGenerated) {
        return <Redirect to="/action" />;
    }

    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header closeButton>
                    <Modal.Title>Attorneys</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    Please select the attorney that you will be filing for:
                    <Form.Control as="select" id="attorneyNames" value={attorneyKey} onChange={(e) => setAttorneyKey(e.target.value)}>
                        <option>Select one</option>
                        {attorneyData.map(item => (
                            <option value={item.pk} key={item.pk}>{item.name}</option>
                        ))}
                    </Form.Control>
                </Modal.Body>

                <Modal.Footer>
                    <Button id="cancelButton" variant="outline-secondary" onClick={returnLogin}>Cancel</Button>
                    <Button id="submitButton" onClick={choseAttorney}>Select</Button>
                    {isError && <div>Please select an attorney</div>}
                </Modal.Footer>
            </Modal.Dialog>
        </div>
    );
}
