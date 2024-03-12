import axios from 'axios';

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Modal, Col, Row, Table, Alert } from 'react-bootstrap';

import { useAuth } from '../../context/auth';

export default function SearchPage() {
    const { authTokens } = useAuth();

    // searchResults is an of Petition Fields, per the api glossary.
    // null indicates that a search has not yet been performed.
    const [searchResults, updateSearchResults] = useState(null);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState(null);

    const accessToken = authTokens?.access;
    function handleSearch(firstName, lastName) {
        const config = {
            "headers": { "Authorization": "Bearer " + accessToken },
            params: {
                first_name: firstName,
                last_name: lastName
            }
        };
        const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.1/pa_court_archive/search/";

        setBusy(true);
        setError(null);

        axios.get(url, config).then(res => {
            console.debug(res);
            if (res.status === 200) {
                updateSearchResults(res.data);
            } else {
                console.error("Search failed: ");
                console.error(res);
                throw new Error(`Search failed with status ${res.status}`);
            }
        }).catch(err => {
            setError(err.message);
            console.error(err)
        }).finally(() => {
            setBusy(false);
        });
    }

    return (
        <Row>
            <Col md={{ span: 6, offset: 3 }}>
                <div>
                    <SearchForm handleSearch={handleSearch} />
                    {busy ?
                        <SearchSpinner /> : (error ?
                            <>
                                <Row><Col>
                                    <Alert variant="danger">
                                        <Alert.Heading>Error</Alert.Heading>
                                        <p>
                                            {error}
                                        </p>
                                    </Alert>
                                </Col></Row>
                            </> :
                            <SearchResults searchResults={searchResults} />)}
                </div>
            </Col>
        </Row>
    );
}

function SearchForm(props) {
    /*
    Props expects:
    
    - handleSearch(firstName, lastName): A function that will execute the
      search and update the SearchPage.
    */

    const [firstName, setSearchFirstName] = useState("");
    const [lastName, setSearchLastName] = useState("");

    function executeSearch() {
        props.handleSearch(firstName, lastName);
    }

    return (
        <div>
            <Modal.Dialog>
                <Modal.Header>
                    <Modal.Title>Search by Name</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Col>
                        First Name: <input name="search_first_name" onChange={e => { setSearchFirstName(e.target.value); }} />
                    </Col>
                    <Col>
                        Last Name: <input name="search_last_name" onChange={e => { setSearchLastName(e.target.value); }} />
                    </Col>
                </Modal.Body>

                <Modal.Footer>
                    <Button id="submitNameButton" onClick={executeSearch}>Search</Button>
                </Modal.Footer>
            </Modal.Dialog>
        </div>
    );
}

function SearchResults(props) {
    /*
    props expects:
    - searchResults: An array of petition field objects, as documented in the glossary.
    */

    function NoResults() {
        return (
            <Row><Col><p>No matches found.</p></Col></Row>
        );
    }

    function SearchTable(props) {
        /*
            props expects:
            - searchResults: An array of petition field objects.
        */
        return (
            <Table>
                <thead><tr>
                    <th>Name</th>
                    <th>Birthdate</th>
                    <th>OTN</th>
                </tr></thead>
                <tbody>
                    {props.searchResults.map((petitionFields, key) => (
                        <SearchRow petitionFields={petitionFields} key={key} />
                    ))}
                </tbody>
            </Table>
        );
    }

    function SearchRow(props) {
        /* props expects:
            - key: identifier
            - petitionFields: the petition fields.
        */
        return (
            <tr key={props.key}>
                <td>{props.petitionFields.petitioner.name}</td>
                <td>{props.petitionFields.petitioner.dob}</td>
                <td>{props.petitionFields.petition.otn}</td>
                <td><Link to={{ "pathname": "/generate", "state": { "petitionFields": props.petitionFields } }}>Create Petition</Link></td>
            </tr>
        );
    }

    if (!Array.isArray(props.searchResults)) {
        // null means you haven't search yet
        return (<></>);
    }
    else if (props.searchResults.length === 0) {
        return (<NoResults />);
    } else {
        return (<SearchTable searchResults={props.searchResults} />);
    }
}

function SearchSpinner() {
    return (
        <Row><Col md={{ span: 2, offset: 5 }}>
            <div class="spinner-border" role="status">
                <span class="sr-only">Loading...</span>
            </div>
        </Col></Row>
    );
}