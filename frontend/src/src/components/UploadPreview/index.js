import React, { useState, useReducer } from "react";
import { useHistory } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../../context/auth";
import Petitioner from "../GeneratePage/components/Petitioner";
import { Button, Form, Row, Col } from "react-bootstrap";

export default function UploadPreview(props) {
	const history = useHistory();

	const [uploadedFiles, setUploadedFiles] = useState([]);
	const [fileNames, setFileNames] = useState([]);
	const [isError, setIsError] = useState(false);
	const { authTokens } = useAuth();

	const fileNameList = fileNames.map((name) => {
		return <li key={name}>{name}</li>;
	});

	const defaultPetitionFields = {
		petitioner: {
			name: "",
			aliases: [],
			dob: "",
			ssn: "",
			address: {
				street1: "",
				street2: "",
				city: "",
				state: "",
				zipcode: "",
			},
		},
		petition: {
			otn: "",
			judge: "",
			ratio: "full",
		},
		dockets: [],
		charges: [],
		fines: {
			total: 0,
			paid: 0,
		},
	};

	// On click for the cancel button
	function returnToChooseAction() {
		history.push("/");
	}

	function mergeReduce(initial, changes) {
		return { ...initial, ...changes };
	}

	const fieldsFromRouterState =
		props.location && props.location.state
			? props.location.state.petitionFields
			: null;
	let petitionFields =
		fieldsFromRouterState || props.petitionFields || defaultPetitionFields;

	const [petitioner, setPetitioner] = useReducer(
		mergeReduce,
		petitionFields.petitioner
	);

	return (
		<Form className='generator'>
			<Petitioner
				{...petitioner}
				handleChange={setPetitioner}
				disabled={false}
			/>
		</Form>
	);
}
