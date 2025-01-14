import React from "react";
import { useHistory } from 'react-router-dom';
import { Button, Card, ListGroup, Row, Table } from "react-bootstrap";
import { usePetitioner } from "../../../context/petitioner";
import { usePetitions } from "../../../context/petitions";
import "./../style.css";


export default function PetitionSummary(props) {
    const history = useHistory();
    const { petitioner } = usePetitioner();
    const { petitions, setPetitionNumber } = usePetitions();
    const {docket_info, docket_numbers, charges, fines} = props.petition;

    const docketNumbers = docket_numbers.map((num, index) => {
        return <ListGroup.Item className="p-0" key={index}>{num}</ListGroup.Item>
    })

    const chargeRows = charges.map((charge, index) => {
        return (
            <tr key={index}>
                <td className="p-0 pl-2 pr-2">{charge.statute}</td>
                <td className="p-0 pl-2 pr-2">{charge.description}</td>
                <td className="p-0 pl-2 pr-2">{charge.grade}</td>
                <td className="p-0 pl-2 pr-2">{charge.disposition}</td>
                <td className="p-0 pl-2 pr-2">{charge.date}</td>
            </tr>
        )
    })

    function editPetition() {
        setPetitionNumber(props.petitionNumber)
        history.push('/generate', {"petitionFields": {
            petitioner,
            petitions
        }})
        window.scrollTo(0, 0)
    }

    function generatePetition() {
        props.postGeneratorRequest(petitioner, props.petition)
        .then((petitionUrl) => {
            if (petitionUrl !== undefined) {
                let filename = `petition_${props.petitionNumber+1}.docx`;
                let a = document.createElement("a");
        
                if (typeof a.download === "undefined") {
                    window.location.href = petitionUrl;
                } else {
                    a.href = petitionUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                }
            }
        })
        .catch((error) => {
            console.error("Error generating petition: ", error);
        })
    }

    return (
        <Card className="mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
                <Card.Title className="m-0">Petition {props.petitionNumber + 1}</Card.Title>
                <div>
                    <Button 
                        onClick={editPetition}
                        variant="outline-primary"
                        className="mr-2"
                        size="sm"
                    >
                        Edit
                    </Button>
                    <Button 
                        onClick={generatePetition}
                        variant="outline-primary"
                        size="sm"
                    >
                        Generate
                    </Button>
                </div>
            </Card.Header>
            <Card.Body>
                <Row >
                    <Table size="sm" className="w-100">
                        <thead>
                            <tr>
                                <th className="p-0 pl-2 pr-2" style={{ width: "30%" }}>Docket Numbers</th>
                                <th className="p-0 pl-2 pr-2" style={{ width: "20%" }}>OTN</th>
                                <th className="p-0 pl-2 pr-2" style={{ width: "30%" }}>Fines</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td className="p-2">
                                    <ListGroup variant="flush">
                                        {docketNumbers}
                                    </ListGroup>
                                </td>
                                <td className="p-2">
                                    {docket_info.otn || "N/A"}
                                </td>
                                <td className="p-2">
                                    <ListGroup variant="flush">
                                        <ListGroup.Item className="p-0">{`Paid Fines: $${fines.paid}`}</ListGroup.Item>
                                        <ListGroup.Item className="p-0">{`Total Fines: $${fines.total}`}</ListGroup.Item>
                                    </ListGroup>
                                </td>
                            </tr>
                        </tbody>
                    </Table>
                </Row>
                <Row>
                    <Table>
                        <thead>
                            <tr>
                                <th className="p-0 pl-2 pr-2">Statute</th>
                                <th className="p-0 pl-2 pr-2">Description</th>
                                <th className="p-0 pl-2 pr-2">Grade</th>
                                <th className="p-0 pl-2 pr-2">Disposition</th>
                                <th className="p-0 pl-2 pr-2">Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {chargeRows}
                        </tbody>
                    </Table>
                </Row>
            </Card.Body>
        </Card>
    )
}