import React, { useState } from "react";
import { Button, Col, Modal } from 'react-bootstrap';
import axios from 'axios';

import { initialPetitionerState, usePetitioner } from "../../../context/petitioner";
import { usePetitions } from "../../../context/petitions";
import { useAuth } from "../../../context/auth";

export default function UploadModal(props) {
    const { isError, setIsError, show, handleClose } = props
    const { authTokens } = useAuth();
    const { petitioner, setPetitioner } = usePetitioner();
    const { setPetitions, setPetitionNumber } = usePetitions();
    
    const [uploadedFiles, setUploadedFiles] = useState([]);

    // list of uploaded files with option to remove file from list
    const fileNameList = uploadedFiles ? uploadedFiles.map((file, idx) => {
        return (
            <li key={file.name}>
                <span>{file.name}</span>
                <Button 
                    variant="danger" 
                    size="sm"
                    onClick={() => removeFile(idx)}
                >
                    X
                </Button>
            </li>
        )
    }) : null;

    // Check file type is PDF
    function checkFileType(file) {
        if (file.type === "application/pdf") {
            return file
        } else {
            alert("Uploaded documents must be PDF files");
        }
    }

    // POST to send PDF files
    function postDocketParser() {

        // Need to check if a file is chosen
        if (uploadedFiles === undefined || uploadedFiles.length === 0) {
            setIsError(true);
        }
        else {
            let pdfdata = new FormData();
            pdfdata.append('name', 'docket_file');
            for (let file of uploadedFiles) {
                pdfdata.append('docket_file', file);
            }

            let petitionerData = (petitioner !== initialPetitionerState)
                ? petitioner
                : null;
            pdfdata.append('petitioner', JSON.stringify(petitionerData));

            // post to generate profile
            const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/parse-docket/";
            const token = `Bearer ${authTokens.access}`;
            var config = {
                'headers': { 'Authorization': token }
            };

            axios.post(url, pdfdata, config)
                .then(res => {
                    if (res.status === 200) {
                        console.log("Ready to generate ..!");
                        console.info(res.data);
                        setPetitions(res.data.petitions)

                        // If the new petitioner is the same as the previous one, copy as much data as we can from the previous one
                        if (res.data.petitioner !== null && petitioner !== null && res.data.petitioner.name === petitioner.name) {
                            let newPetitioner = {};
                            newPetitioner.name = res.data.petitioner.name;
                            if (res.data.petitioner.aliases !== null) {
                                let aliasesSet = new Set(res.data.petitioner.aliases.concat(petitioner.aliases));
                                newPetitioner.aliases = [...aliasesSet];
                            } else {
                                newPetitioner.aliases = petitioner.aliases;
                            }

                            newPetitioner.dob = res.data.petitioner.dob || petitioner.dob;
                            newPetitioner.ssn = petitioner.ssn;
                            newPetitioner.address = petitioner.address;
                            setPetitioner(newPetitioner);
                            res.data.petitioner = newPetitioner;
                        } else {
                            setPetitioner(res.data.petitioner);
                        }
                        
                        setPetitionNumber(0)
                        handleClose()
                    }})
                .catch(err => {
                    console.error(err);
                });
        }
    }

    // Add new files
    function uploadDocs(docs) {
        const newFiles = Array.from(docs, checkFileType).filter(file => file !== undefined);
        const newFileNames = new Set(newFiles.map((file) => file.name));
        const oldUniqueFiles = uploadedFiles.filter((file) => !newFileNames.has(file.name));
        setUploadedFiles([...oldUniqueFiles, ...newFiles]);
    }

    function removeFile(idx) {
        setUploadedFiles(uploadedFiles.filter((_, index) => index !== idx))
    }

    return (
        <Modal show={show} onHide={handleClose} >
            <Modal.Header closeButton >
                <Modal.Title>Upload Files</Modal.Title>
            </Modal.Header>

            <Modal.Body>
                <Col>
                    <input 
                        type="file" 
                        name="docket_file" 
                        multiple 
                        accept=".pdf" 
                        onChange={e => { uploadDocs(e.target.files); }}
                    />
                    <ul style={{listStyleType: "none"}}>{fileNameList}</ul>
                    {isError && <div className="alert alert-warning" role="alert">Please select a file</div>}
                </Col>
            </Modal.Body>

            <Modal.Footer>
                <Button id="fileButton" onClick={postDocketParser}>Submit</Button>
            </Modal.Footer>
        </Modal>
    )
}