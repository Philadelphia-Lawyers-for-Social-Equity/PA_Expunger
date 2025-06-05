import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Alert, Button, Card, Container } from 'react-bootstrap';

import { usePetitioner } from '../../context/petitioner';
import { initialPetitionState, usePetitions } from '../../context/petitions';
import { useUser } from '../../context/user';
import Attorney from './components/Attorney';
import Petitioner from '../GeneratePage/components/Petitioner';
import PetitionTable from './components/PetitionTable';
import Organization from './components/Organization';
import UploadModal from './components/UploadModal';

export default function FileUpload(props) {
    const history = useHistory();
    const { user } = useUser();
    const { petitioner } = usePetitioner();
    const { petitions, setPetitions } = usePetitions();
    
    const [doNotGenerate, setDoNotGenerate] = useState([]);
    const [pageError, setPageError] = useState("");
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [petitionCount, setPetitionCount] = useState(0);

    const handleClose = () => setShowUploadModal(false);
    const handleShow = () => {
        setPageError("");
        setShowUploadModal(true);
    }


    function continuePetitionGeneration() {
        // remove petitions from array if user has selected to omit them
        const petitionsToGenerate = petitions.filter(petition => {
            if (petition.docket_info.otn && doNotGenerate.includes(petition.docket_info.otn)) {
                return false
            }
            for (const num of petition.docket_numbers) {
                if (doNotGenerate.includes(num)) {
                    return false
                }
            }
            return true
        })
        setPetitions(petitionsToGenerate)
        history.push("/generate", {"petitionFields": {petitions: petitionsToGenerate, petitioner}});
    }

    // show upload modal when page first loads and/or no petitions have been uploaded
    useEffect(() => {
        if (petitions === initialPetitionState) {
            handleShow()
        }
        // eslint-disable-next-line
    }, [])

    return (
        <div>
            <Container fluid className="pt-4">
                <div className="d-flex justify-content-between mb-4">
                    <h4>Petition Generation Preview</h4>
                    <div >
                        <Button 
                            className="me-2 d-inline"
                            onClick={handleShow}
                        >
                            Upload Files
                        </Button>
                        <Button
                            className="me-2 d-inline"
                            onClick={continuePetitionGeneration}
                            disabled={petitionCount < 1}
                        >
                            Continue to Petition Generation
                        </Button>
                    </div>
                </div>

                {(petitions === initialPetitionState) && <Alert
                    variant="warning"
                    className="justify-content-md-center text-center mb-4"
                >
                    Upload a Court Docket or Court Summary to begin petition generation.
                </Alert>}
                {pageError && <Alert
                    variant="danger"
                    className="justify-content-md-center text-center mb-4"
                >
                    {pageError}
                </Alert>}

                <Organization organization={user.organization}/>

                <Attorney attorney={user.attorney}/>

                <Card className="mb-4">
                    <Card.Header as="h5" className="ps-3">
                        Petitioner
                    </Card.Header>
                    <Card.Body className="ps-0">
                        <Petitioner {...petitioner} preview={true}/>
                    </Card.Body>

                </Card>

                <PetitionTable 
                    doNotGenerate={doNotGenerate}
                    setDoNotGenerate={setDoNotGenerate}
                    petitionCount={petitionCount}
                    setPetitionCount={setPetitionCount}
                />
            </Container>

            <UploadModal
                handleClose={handleClose}
                show={showUploadModal}
                setPageError={setPageError}
            />
        </div >
    );
}
