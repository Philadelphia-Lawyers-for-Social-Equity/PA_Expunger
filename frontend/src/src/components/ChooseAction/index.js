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
                        <Col sm={2}> </Col>
                        <Col sm={4}>   
                            <Button id="searchButton" onClick={redirectToSearch}>Search Archive</Button>
                        </Col>
                        <Col sm={4}>
                            <Button id="uploadButton" onClick={redirectToUpload}>Upload Docket</Button>
                        </Col>
                        <Col sm={2}> </Col>
                    </Row>
                </Modal.Body>

                <Modal.Footer>
                </Modal.Footer>
            </Modal.Dialog>
        </div>
    );
}
