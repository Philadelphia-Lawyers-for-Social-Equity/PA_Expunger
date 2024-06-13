import React, { useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';

export default function RemovableCharge(props) {
    /* props expects:
        - label
        - statute
        - description
        - grade
        - date
        - disposition
        - handleChange
        - handleRemove

    */

    const [statute, setStatute] = useState(props.statute || "");
    const [description, setDescription] = useState(props.description || "");
    const [grade, setGrade] = useState(props.grade || "");
    const [date, setDate] = useState(props.date || "");
    const [disposition, setDisposition] = useState(props.disposition || "");

		const [readOnly, setReadOnly] = useState(true);

    function save() {
        props.handleChange({
            "statute": statute,
            "description": description,
            "grade": grade,
            "date": date,
            "disposition": disposition,
            "key": description
        });
    }

    return (
        <Row className="mb-2">
					<Col xs={1} className="py-1 d-flex flex-column">
							<Button className="mt-4 mb-2"
								variant={readOnly ? 'secondary' : 'success'}
								onClick={(e) => {
									if (!readOnly) {
										save();
									}
									setReadOnly(!readOnly); 
								}}
							>{readOnly ? 'Edit' : 'Save'}</Button>
							<Button variant="danger" className="mb-4"
                onClick={ props.handleRemove }
                disabled={props.disabled || false}
							>Remove</Button>
					</Col>
					<Col xs={7}>
						<Row className="mb-2">
							<Form.Group className="col-3 px-0 mx-2 mb-0" controlId="statute">
								<Form.Label className="mb-0"><strong>Statute</strong></Form.Label>
								<Form.Control className="col"
                  placeholder="Statute"
                  value={statute}
                  onChange={(e) => {setStatute(e.target.value);}}
                  disabled={props.disabled || false}
									readOnly={readOnly}
								/>
							</Form.Group>
							<Form.Group className="col-1 px-0 mx-2 mb-0" controlId="grade"> 
								<Form.Label className="mb-0"><strong>Grade</strong></Form.Label>
								<Form.Control className="col"
									placeholder="grade"
                  value={grade}
                  onChange={(e) => {setGrade(e.target.value);}}
                  disabled={props.disabled || false}
									readOnly={readOnly}
								/>
							</Form.Group>
							<Form.Group className="col-3 px-0 mx-2 mb-0" controlId="date">
								<Form.Label className="mb-0"><strong>Date</strong></Form.Label>
								<Form.Control className="col"
									type="date"
                  value={date}
                  onChange={(e) => {setDate(e.target.value);}}
									disabled={props.disabled || false}
									readOnly={readOnly}
                />
							</Form.Group>
							<Form.Group className="col-4 px-0 mx-2 mb-0" controlId="disposition"> 
								<Form.Label className="mb-0"><strong>Disposition</strong></Form.Label>
								<Form.Control className="col"
									placeholder="Disposition"
                  value={disposition}
									onChange={(e) => {setDisposition(e.target.value);}}
                  disabled={props.disabled || false}
									readOnly={readOnly}
                />
							</Form.Group>
						</Row>
						<Form.Group className="row px-2" controlId="description">
							<Form.Label className="mb-0"><strong>Description</strong></Form.Label>
							<Form.Control
                  value={description}
                  onChange={(e) => {setDescription(e.target.value);}}
                  disabled={props.disabled || false}
									readOnly={readOnly}
                />
						</Form.Group>	
					</Col>
				</Row>
    );
}
