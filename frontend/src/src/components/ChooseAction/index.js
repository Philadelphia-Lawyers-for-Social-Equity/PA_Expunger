import React from "react";
import { useHistory } from 'react-router-dom';
import "./style.css";
//import axios from 'axios';
import { Button, Modal, Row, Col } from 'react-bootstrap';


export default function ChooseAction() {
    const history = useHistory();

    // On click to search module
    function redirectToSearch() {
        history.push("/search");
    }

    // On click to upload pdf module
    function redirectToUpload() {
        history.push("/upload");
    }

    return (
        <div className="text-center">
            <Modal.Dialog>
                <Modal.Header>
                    <Modal.Title>Select how to generate a petition</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Row>
                        <Col sm={1}> </Col>
                        <Col sm={5}>   
                            <Button disabled id="searchButton" className="option-btn" onClick={redirectToSearch}>Search Archive</Button>
                        </Col>
                        <Col sm={5}>
                            <Button id="uploadButton" className="option-btn" onClick={redirectToUpload}>Upload Document</Button>
                        </Col>
                        <Col sm={1}> </Col>
                    </Row>
                </Modal.Body>            

                <Modal.Footer>
                    Uploaded documents must be PDF files of Pennsylvania Court Summaries or Court Dockets
                </Modal.Footer>
            </Modal.Dialog>
        </div>
    );
}
