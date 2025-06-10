import React, { useEffect, useState } from "react";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import { Button, Card, Container, ListGroup } from 'react-bootstrap';
import { useHistory } from "react-router-dom";
import PetitionSummary from "./components/PetitionSummary";
import { useUser } from '../../context/user';
import { initialPetitionerState, usePetitioner } from "../../context/petitioner";
import { initialPetitionState, usePetitions } from "../../context/petitions";
import "./style.css";
import api from "../../services/api";
import { useAuth } from "../../context/auth";
import { useIsMounted } from "../../hooks/useIsMounted";

const initialSummary = {
    name: "",
    dob: "",
    actions: {
        partial: 0,
        full: 0,
    },
    petitionSummaries: [
        {
            docket_numbers: [],
            otn: "",
            action: "",
            error: false,
        },
    ],
};

export default function ReviewPage(props) {
    const history = useHistory();
    const { authenticatedRequest } = useAuth();
    const { user } = useUser();
    const { petitioner, setPetitioner } = usePetitioner();
    const { petitions, setPetitions } = usePetitions();
    const [ summary, setSummary ] = useState(initialSummary);
    const getIsMounted = useIsMounted();
    
    useEffect(() => {
        try {
            // re-create petitions state from history after page refresh
            if (petitions === initialPetitionState) {
                setPetitions(props.location.state.petitionFields.petitions)
            }
            if (petitioner === initialPetitionerState) {
                setPetitioner(props.location.state.petitionFields.petitioner);
            }
            window.scrollTo(0, 0)
        } catch {
            // TODO: proper error handling
            history.push("/");
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
        // create data for generation of petitions summary
        let partial = 0
        let full = 0
        const petitionSummaries = (petitions && Array.isArray(petitions)) ? petitions.map(petition => {
            if (petition.docket_info.ratio === "full") {
                full++;
            } else {
                partial++;
            }
            return {
                docket_numbers: petition.docket_numbers,
                otn: petition.docket_info.otn,
                action: petition.docket_info.ratio,
                error: false,
            }
        }) : null;
            
        setSummary({
            name: petitioner.name,
            dob: petitioner.dob,
            actions: {
                partial,
                full,
            },
            petitionSummaries,
        })
    }, [petitioner, petitions])

    async function postGeneratorRequest(petitioner, petition, index) {
        let petitionFields = {
            petitioner: petitioner,
            petition: { ...petition.docket_info, date: today() },
            dockets: petition.docket_numbers,
            charges: petition.charges,
            fines: petition.fines,
            organization: user.organization,
            attorney: user.attorney,
        };
    
        if (!petitionFields.petition.ratio) {
            petitionFields.petition.ratio = "full";
        }

        console.info("Requesting petition with this data:", petitionFields);
        try {
            const blob = await authenticatedRequest(() => api.generatePetitionBlob(petitionFields));
            return window.URL.createObjectURL(blob);
        } catch {
            setSummaryError(index);
        }
    }

    function generatePetitions() {
        return Promise.all(petitions.map(async (petition, idx) => {
            return await postGeneratorRequest(petitioner, petition, idx)
        }))
    }

    async function postSummaryRequest() {
        try {
            let blob = await authenticatedRequest(() => api.generatePetitionSummaryBlob(summary));
            return window.URL.createObjectURL(blob)
        } catch (e) {
            // Additional error handling goes here
        }
    }

    function setSummaryError(errorIndex) {
        if (!getIsMounted()) return;
        const newPetitionSummaries = summary.petitionSummaries.map((sum, idx) => {
            if (errorIndex === idx) {
                sum.error = true;
                return sum
            } else {
                return sum
            }
        })
        setSummary({
            ...summary,
            petitionSummaries: newPetitionSummaries
        })
    }

    async function saveToZip() {
        const zip = new JSZip();
        const folder = zip.folder('petitions');
        const petitionUrls = await generatePetitions();

        // Fetch each petition and add it to the zip as a .docx file
        await Promise.allSettled(
            petitionUrls.map(async (petitionUrl, index) => {
                if (petitionUrl !== undefined) {
                    try {
                        const response = await fetch(petitionUrl);
                        if (response.status === 200) {
                            const blob = await response.blob();
                            const name = `petition-${petitioner.name}-${index+1}.docx`;
                            folder.file(name, blob, { binary: true });
                        } else {
                            console.error(`Failed to fetch ${petitionUrl}: ${response.statusText}`);
                            setSummaryError(index);
                        }
                    } catch (error) {
                        console.error(`Error fetching ${petitionUrl}: ${error}`);
                        setSummaryError(index);
                    }
                } else {
                    console.error(`Error fetching petition ${index}`);
                }
            })
        );

        const summaryUrl = await postSummaryRequest();
        if (!getIsMounted()) return;

        if (summaryUrl) {
            try {
                const response = await fetch(summaryUrl);
                if (response.status === 200) {
                    const blob = await response.blob();
                    const name = `report-${petitioner.name}.docx`;
                    console.log("adding summary to folder")
                    folder.file(name, blob, { binary: true });
                } else {
                    console.error(`Failed to fetch ${summaryUrl}: ${response.statusText}`);
                }
            } catch (error) {
                console.error(`Error fetching ${summaryUrl}: ${error}`);
            }
        }

        // Generate and save the zip file
        zip.generateAsync({type:"blob"})
            .then(blob => saveAs(blob, 'petitions.zip'))
            .catch(e => console.error(e))
    }

    if (petitions === initialPetitionState || petitioner === initialPetitionerState) {
        return null
    }

    const petitionSummaries = (petitions && petitions.docket_numbers !== initialPetitionState) ? petitions.map((petition, index) => {
        return <PetitionSummary key={index} petitionNumber={index} petition={petition} postGeneratorRequest={postGeneratorRequest} />
    }) : null;

    return (
        <Container fluid className="pt-4">
            <Card className="mb-4 ">
                <Card.Header as="h5" className="pl-3">Petitioner</Card.Header>
                <ListGroup variant="flush">
                    <ListGroup.Item className="p-0 pl-3 pt-2">{"Name: " + petitioner.name}</ListGroup.Item>
                    <ListGroup.Item className="p-0 pl-3 pt-2 pb-2">{"Date of Birth: " + petitioner.dob}</ListGroup.Item>
                </ListGroup>
            </Card>
            {petitionSummaries}
            <Button onClick={saveToZip} className="mr-3 mb-3">Download All Petitions</Button>
            <Button href="/" className="mb-3">Start New Petition</Button>
        </Container>
    )
}

function today() {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, "0");
    var mm = String(today.getMonth() + 1).padStart(2, "0");
    var yyyy = today.getFullYear();
    return yyyy + "-" + mm + "-" + dd;
}
