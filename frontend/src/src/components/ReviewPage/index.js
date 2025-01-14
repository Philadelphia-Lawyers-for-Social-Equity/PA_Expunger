import React, { useEffect } from "react";
import JSZip from "jszip";
import axios from "axios";
import { saveAs } from "file-saver";
import { Button, Card, Container, ListGroup } from 'react-bootstrap';
import PetitionSummary from "./components/PetitionSummary";
import { useAuth } from "../../context/auth";
import { initialPetitionerState, usePetitioner } from "../../context/petitioner";
import { initialPetitionState, usePetitions } from "../../context/petitions";
import "./style.css";

const url =
    process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/generate/";

export default function ReviewPage(props) {
    const { authTokens } = useAuth();
    const { petitioner, setPetitioner } = usePetitioner();
    const { petitions, setPetitions } = usePetitions();
    
    useEffect(() => {
        // re-create petitions state from history after page refresh
        if (petitions === initialPetitionState) {
            setPetitions(props.location.state.petitionFields.petitions)
        }
        if (petitioner === initialPetitionerState) {
            setPetitioner(props.location.state.petitionFields.petitioner);
        }
        window.scrollTo(0, 0)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    function postGeneratorRequest(petitioner, petition) {
        let petitionFields = {
            petitioner: petitioner,
            petition: { ...petition.docket_info, date: today() },
            dockets: petition.docket_numbers,
            charges: petition.charges,
            fines: petition.fines,
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

        return axios
            .post(url, petitionFields, postRequestConfig())
            .then((res) => {
                if (res.status === 200) {
                    let blob = new Blob([res.data], {
                        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    });
                    const petitionUrl = window.URL.createObjectURL(blob)
                    return petitionUrl
                }
            })
            .catch((error) => {
                console.error(error);
            });
    }

    function generatePetitions() {
        const petitionUrls = Promise.all(petitions.map(petition => {
            return postGeneratorRequest(petitioner, petition)
        }))
        return petitionUrls
    }

    async function saveToZip() {
        const zip = new JSZip();
        const folder = zip.folder('petitions')
        const petitionUrls = await generatePetitions()

        // Fetch each petition and add it to the zip as a .docx file
        await Promise.all(
            petitionUrls.map(async (petitionUrl, index) => {
                try {
                    const response = await fetch(petitionUrl);
                    if (response.status === 200) {
                        const blob = await response.blob();
                        const name = `petition-${index+1}.docx`;
                        folder.file(name, blob, { binary: true });
                    } else {
                        console.error(`Failed to fetch ${petitionUrl}: ${response.statusText}`);
                    }
                } catch (error) {
                    console.error(`Error fetching ${petitionUrl}: ${error}`);
                }
            })
        );
    
        // Generate and save the zip file
        zip.generateAsync({type:"blob"})
            .then(blob => saveAs(blob, 'petitions.zip'))
            .catch(e => console.log(e))
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
            <Button href="/action" className="mb-3">Start New Petition</Button>
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