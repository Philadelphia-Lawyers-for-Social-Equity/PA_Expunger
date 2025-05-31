import React, { useRef, useState } from "react";
import { Button, Col, Modal } from 'react-bootstrap';

import api from "../../../services/api";
import { initialPetitionerState, usePetitioner } from "../../../context/petitioner";
import {initialPetitionState, usePetitions} from "../../../context/petitions";
import {useIsMounted} from "../../../hooks/useIsMounted";

export default function UploadModal(props) {
    const { show, setPageError, handleClose } = props;
    const { petitioner, setPetitioner } = usePetitioner();
    const { setPetitions, setPetitionNumber } = usePetitions();

    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [modalError, setModalError] = useState("");

    const getIsMounted = useIsMounted();
    const fileInputRef = useRef(null);

    // list of uploaded files with option to remove file from list
    const fileNameList = uploadedFiles && uploadedFiles.length > 0 ? uploadedFiles.map((file, idx) => {
        return (
            <li key={file.name} className="list-group-item d-flex justify-content-between align-items-center py-1 px-2">
                <span>{file.name}</span>
                <Button 
                    variant="danger" 
                    size="sm"
                    onClick={() => removeFile(idx)}
                    className="flex-shrink-0"
                    aria-label={`Remove ${file.name}`}
                    title={`Remove ${file.name}`}
                >
                    X
                </Button>
            </li>
        )
    }) : null;

    // Send PDFs and petitioner data to backend for parsing
    async function handleSubmitFiles() {
        // Need to check if a file is chosen
        if (uploadedFiles.length === 0) {
            setModalError("Please select at least one file to upload.");
            return;
        }
        setPageError("");
        setModalError("");

        let formData = new FormData();
        let petitionerData = (petitioner !== initialPetitionerState)
            ? petitioner
            : null;
        formData.append('petitioner', JSON.stringify(petitionerData));
        for (let file of uploadedFiles) {
            formData.append('docket_file', file);
        }

        try {
            const data = await api.parseDocket(formData);
            console.debug("Received parsed data:", data);
            setPetitions(data.petitions || initialPetitionState);
            // If the new petitioner is the same as the previous one, copy as much data as we can from the previous one
            if (data.petitioner && petitioner !== null && data.petitioner.name === petitioner.name) {
                let newPetitioner = {};
                newPetitioner.name = data.petitioner.name;
                if (data.petitioner.aliases !== null) {
                    let aliasesSet = new Set(data.petitioner.aliases.concat(petitioner.aliases));
                    newPetitioner.aliases = [...aliasesSet];
                } else {
                    newPetitioner.aliases = petitioner.aliases;
                }

                newPetitioner.dob = data.petitioner.dob || petitioner.dob;
                newPetitioner.ssn = petitioner.ssn;
                newPetitioner.address = petitioner.address;
                setPetitioner(newPetitioner);
                data.petitioner = newPetitioner;
            } else {
                setPetitioner(data.petitioner || initialPetitionerState);
            }
            setPetitionNumber(0);
            if (getIsMounted()){
                handleClose();
            }
        } catch (e) {
            let displayErrorMessage;
            if (e.response) {
                const errorData = e.response.data;
                const headers = e.response.headers || {};
                const contentType = String(headers['content-type'] || '').toLowerCase();
                if (typeof errorData === 'string' && errorData.trim() !== '') {
                    displayErrorMessage = errorData;
                } else if (contentType.includes('text/html')) {
                    displayErrorMessage = "The server returned an unexpected HTML page " +
                        `(status ${e.response.status}). Check the developer console for details.`;
                } else if (contentType.includes('application/json') && errorData) {
                    if (errorData.detail) {
                        displayErrorMessage = errorData.detail;
                    } else {
                        displayErrorMessage = `Unexpected error: ${JSON.stringify(errorData)}`
                    }
                } else {
                    displayErrorMessage = `An error occurred on the server (status ${e.response.status}). Please try again.`;
                }
            } else if (e.request) {
                displayErrorMessage = e.message || "Could not connect to the server. Please check your network and try again.";
            } else {
                displayErrorMessage = e.message || "An error occurred before the request could be sent.";
            }

            setPageError(displayErrorMessage);
            if (getIsMounted()){
                handleClose();
            }
        }
    }

    // On change for file input. Assumes all filenames are unique.
    function handleSelectFiles(selectedFileList) { // this will be a FileList
        setModalError("");

        if (!selectedFileList || selectedFileList.length === 0) {
            return;
        }
        const selectedFilesArray = Array.from(selectedFileList);
        const validPdfArray = [];
        const invalidSelectedFileNames = [];
        // Validate type of selected files
        for (const file of selectedFilesArray) {
            if (file.type === "application/pdf") {
                validPdfArray.push(file);
            } else {
                invalidSelectedFileNames.push(file.name);
            }
        }

        if (invalidSelectedFileNames.length > 0) {
            const errorMsg = "The following selected file(s) are not PDFs and were not added: " +
                `${invalidSelectedFileNames.join(", ")}. Please select PDF files only.`;
            setModalError(errorMsg);
            return;
        }

        let updatedCombinedFiles = [...uploadedFiles];

        for (const newFile of validPdfArray) {
            const existingFileIndex = updatedCombinedFiles.findIndex(
                (existingFile) => existingFile.name === newFile.name
            );

            if (existingFileIndex === -1) {
                // New file name not already in list
                updatedCombinedFiles.push(newFile);
            } else {
                // Replace existing file with new file with same name
                updatedCombinedFiles[existingFileIndex] = newFile;
            }
        }
        setUploadedFiles(updatedCombinedFiles);
    }

    function removeFile(idxToRemove) {
        setUploadedFiles(currentFiles => {
            return currentFiles.filter((_, index) => index !== idxToRemove);
        });
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
                        onChange={e => {
                            handleSelectFiles(e.target.files);
                        }}
                        ref={fileInputRef}
                        style={{display: 'none'}} // Hide the default input element
                    />

                    <button
                        className="btn btn-primary mb-3"
                        type="button"
                        onClick={() => {
                            if (fileInputRef.current) {
                                fileInputRef.current.click();
                            }
                        }}
                    >
                        Choose Files
                    </button>
                    {fileNameList && fileNameList.length > 0 && (
                        <ul className="list-group mt-2">{fileNameList}</ul>
                    )}

                    {modalError && (
                        <div className="alert alert-danger mt-2" role="alert">
                            {modalError}
                        </div>
                    )}
                </Col>
            </Modal.Body>

            <Modal.Footer>
                <Button id="fileButton" onClick={handleSubmitFiles}>Submit</Button>
            </Modal.Footer>
        </Modal>
    )
}
