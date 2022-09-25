import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, Modal, Col } from 'react-bootstrap';


export default function FileUpload() {

    const history = useHistory();

    const [fileName, setFileName] = useState(undefined);
    const [isError, setIsError] = useState(false);

    // On click for the cancel button
    function returnToChooseAction() {
        history.push("/action");
    }

    // On change for getting file
    function getFile(files) {
        setFileName(files[0]);
    }

    // POST to send PDF file
    function chooseFile() {

        // Need to check if a file is chosen
        if (fileName === undefined) {
            setIsError(true);
        }
        else {
            let pdfdata = new FormData();
            pdfdata.append('name', 'docket_file');
            pdfdata.append('docket_file', fileName);

            // post to generate profile
            const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/petition/parse-docket/";
            const bearer = "Bearer ";
            const token = bearer.concat(localStorage.getItem("access_token"));
            var config = {
                'headers': { 'Authorization': token }
            };

            axios.post(url, pdfdata, config)
                .then(res => {
                    if (res.status === 200) {
                        console.log("Ready to generate ..!");
                        console.info(res.data);
                        history.push("/generate", {"petitionFields": res.data});
                    }
                })
                .catch(err => {
                    console.error(err);
                });
        }
    }


    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header>
                    <Modal.Title>Upload File</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Col>
                        <input type="file" name="docket_file" onChange={e => { getFile(e.target.files); }} />
                    </Col>
                </Modal.Body>

                <Modal.Footer>
                    <Button id="returnToLoginButton" onClick={returnToChooseAction}>Cancel</Button>
                    <Button id="fileButton" onClick={chooseFile}>Submit</Button>
                    {isError && <div>Please select a file</div>}
                </Modal.Footer>
            </Modal.Dialog>

        </div >
    );
}
