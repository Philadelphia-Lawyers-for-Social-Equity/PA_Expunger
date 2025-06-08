import React, {useCallback, useEffect, useState} from 'react';
import {useHistory} from 'react-router-dom';
import {Button, Form, Modal} from 'react-bootstrap';
import {useAuth} from "../../context/auth";
import api from "../../services/api";
import {useIsMounted} from '../../hooks/useIsMounted'
import {useUser} from "../../context/user";

// TODO: If we add the ability to select an organization, that would happen in this component.

export default function LandingPage() {
    const [attorneyData, setAttorneyData] = useState([]);
    const [attorneyKey, setAttorneyKey] = useState(""); // PK of the selected attorney
    const [isError, setIsError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const {isAuthenticated, authenticatedRequest} = useAuth();
    const {refreshUserProfile} = useUser();
    const history = useHistory();
    const getIsMounted = useIsMounted();

    // Fetches the list of attorneys to populate form options.
    useEffect(() => {
        if (isAuthenticated) {
            (async () => {
                if (getIsMounted()) {
                    setIsError(false);
                    setErrorMessage("");
                }

                try {
                    const data = await authenticatedRequest(() => api.getAttorneys());
                    if (getIsMounted()) {
                        setAttorneyData(data || []);
                        if (data && data.length === 0) {
                            setIsError(true);
                            setErrorMessage("There are no attorneys registered. Please contact an admin.");
                        }
                    }
                } catch (error) {
                    console.error("Failed to load attorneys:", error);
                    if (getIsMounted()) {
                        setIsError(true);
                        setErrorMessage("Failed to load attorneys. Please try again.");
                    }
                }
            })();
        } else if (getIsMounted()) {
            // If not authenticated but the component hasn't been unmounted yet, clear local state.
            setAttorneyData([]);
            setIsError(false);
            setErrorMessage("");
        }

    }, [isAuthenticated, getIsMounted, authenticatedRequest]);

    const handleAttorneyChange = useCallback((event) => {
        setAttorneyKey(event.target.value);
        setIsError(false);
        setErrorMessage("");
    }, []);

    // On click, submits the selected attorney to update the user's profile and navigate to next route
    async function handleSubmit() {
        if (attorneyKey === "" || attorneyKey === "Select one") {
            setIsError(true);
            setErrorMessage("Please select an attorney.");
            return;
        }
        setIsError(false);
        setErrorMessage("");

        const selectedAttorney = attorneyData.find(attorney => `${attorney.pk}` === attorneyKey);

        if (!selectedAttorney) {
            setIsError(true);
            setErrorMessage("Selected attorney not found. Please refresh and try again.");
            console.error("Attorney not found in local data for key:", attorneyKey);
            return;
        }

        const profileData = {
            "attorney": parseInt(attorneyKey),
            "organization": 1,
            "user_id": selectedAttorney.user_id
        };
        try {
            const res = await authenticatedRequest(() => api.updateProfile(profileData));
            console.log("Profile update successful:", res);
            // Currently, we're skipping the /action route because only one action is implemented
            // history.push("/action");
            history.push("/upload");
        } catch (error) {
            console.error("Error updating profile:", error);
            if (getIsMounted()) {
                const serverError = error.response?.data?.detail || error.message || "Unknown error, try again.";
                setIsError(true);
                setErrorMessage(serverError);
            }
        } finally {
            refreshUserProfile();
        }
    }


    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header>
                    <Modal.Title>Attorneys</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    Please select the attorney that you will be filing for:
                    <Form.Control
                        as="select"
                        id="attorneyNames"
                        value={attorneyKey}
                        onChange={handleAttorneyChange}
                        disabled={!attorneyData || attorneyData.length === 0}
                        className="mt-2"
                    >
                        <option value="">Select one</option>
                        {attorneyData?.map(item => (
                            <option value={item.pk} key={item.pk}>{item.name}</option>
                        ))}
                    </Form.Control>
                    {(!attorneyData || attorneyData.length === 0) && !isError && isAuthenticated &&
                        <p className="mt-2">Loading attorneys or no attorneys available...</p>
                    }
                </Modal.Body>

                <Modal.Footer>
                    <Button
                        id="submitButton"
                        onClick={handleSubmit}
                        disabled={!attorneyKey}
                    >
                        Select
                    </Button>
                    {isError && <div style={{
                        color: 'red',
                        width: '100%',
                        textAlign: 'center',
                        marginTop: '10px'
                    }}>{errorMessage}</div>}
                </Modal.Footer>
            </Modal.Dialog>
        </div>
    );
}
