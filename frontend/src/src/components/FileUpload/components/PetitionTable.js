import React, { useEffect, useState } from "react";
import {  Card, Table } from 'react-bootstrap';

import { usePetitioner } from "../../../context/petitioner";
import { initialPetitionState, usePetitions } from "../../../context/petitions";
import PetitionRow from "./PetitionRow";

export default function PetitionTable(props) {
    /*
        props expects:
        - doNotGenerate
        - setDoNotGenerate
        - petitionCount
    */
    const { petitioner } = usePetitioner();
    const { petitions } = usePetitions();
    const { doNotGenerate, setDoNotGenerate, petitionCount, setPetitionCount} = props;
    const [omitCount, setOmitCount] = useState(0);

    // table rows for petition preview
    const petitionList = (petitions !== initialPetitionState) 
        ? petitions.map((petition, idx) => {
            return (
                <PetitionRow 
                    key={idx} 
                    idx={idx} 
                    petition={petition} 
                    name={petitioner.name} 
                    doNotGenerate={doNotGenerate}
                    setDoNotGenerate={setDoNotGenerate}
                    omitCount={omitCount}
                    setOmitCount={setOmitCount}
                />
            )
        }) 
        : null;

    useEffect(() => {
        if (petitionList) {
            setPetitionCount(petitionList.length - omitCount);
        }
        // eslint-disable-next-line
    }, [petitionList, omitCount])

    return (
        <Card className="mb-4">
            <Card.Header as="h5" className="pl-3">
                Petitions
            </Card.Header>
            <Card.Body className="p-0">
                <Card.Text className="p-0 pl-3 pt-2 mb-0">
                    {"Total petitions to generate: " + petitionCount}
                </Card.Text>
                <div className="pt-2 ml-2 mr-2">
                    <Table 
                        borderless
                        striped
                        size="sm"
                    >
                        <thead>
                            <tr>
                                <th style={{ width: '40px' }}></th>
                                <th style={{ width: '40px' }}>#</th>
                                <th style={{ width: '120px' }}>OTN</th>
                                <th style={{ width: '220px' }}>Docket No.</th>
                                {/*<th>Case Name</th>*/}
                                <th style={{ width: '40px' }}>Omit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {petitionList}
                        </tbody>
                    </Table>
                </div>
            </Card.Body>
        </Card>
    )
}
