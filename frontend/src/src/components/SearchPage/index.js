import axios from 'axios';

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Modal, Col, Row, Table } from 'react-bootstrap';

import { useAuth } from '../../context/auth';

export default function SearchPage() {
    const { authedAxios } = useAuth();

    // searchResults is an of Petition Fields, per the api glossary.
    // null indicates that a search has not yet been performed.
    const [searchResults, updateSearchResults] = useState(null);

    function handleSearch(firstName, lastName) {
        const config = { baseURL:  `${process.env.REACT_APP_BACKEND_HOST}/api/v0.2.1` };
        const url = `/pa_court_archive/search/?first_name=${firstName}&last_name=${lastName}`;

        authedAxios.get(url, config).then(res => {
            console.debug(res);
            if (res.status === 200) {
                updateSearchResults(res.data);
            } else {
                console.error("Search failed: ");
                console.error(res);
            }
        }).catch(err => { console.error(err) });
    }

    return (
        <div>
            <SearchForm handleSearch={handleSearch} />
            <SearchResults searchResults={searchResults} />
        </div>
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
