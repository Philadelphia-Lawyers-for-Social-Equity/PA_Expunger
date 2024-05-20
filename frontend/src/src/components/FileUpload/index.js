import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import axios from "axios";
import { Button, Modal, Col } from "react-bootstrap";
import { useAuth } from "../../context/auth";

export default function FileUpload() {
	const history = useHistory();

	const [uploadedFiles, setUploadedFiles] = useState([]);
	const [fileNames, setFileNames] = useState([]);
	const [isError, setIsError] = useState(false);
	const { authTokens } = useAuth();

	const fileNameList = fileNames.map((name) => {
		return <li key={name}>{name}</li>;
	});

	// On click for the cancel button
	function returnToChooseAction() {
		history.push("/");
	}

	// On change for getting files
	function getFile(uploadedDocs) {
		setFileNames([]);
		for (const file of uploadedDocs) {
			setUploadedFiles((files) => [...files, file]);
			if (uploadedDocs.length > 1) {
				setFileNames((nameList) => [...nameList, file.name]);
			}
		}
	}

	// POST to send PDF file
	function chooseFile() {
		// Need to check if a file is chosen
		if (uploadedFiles === undefined) {
			setIsError(true);
		} else {
			let pdfdata = new FormData();
			pdfdata.append("name", "docket_file");
			for (let file of uploadedFiles) {
				pdfdata.append("docket_file", file);
			}

			// post to generate profile
			const url =
				process.env.REACT_APP_BACKEND_HOST +
				"/api/v0.2.0/petition/parse-docket/";
			const token = `Bearer ${authTokens.access}`;
			var config = {
				headers: { Authorization: token },
			};

			axios
				.post(url, pdfdata, config)
				.then((res) => {
					if (res.status === 200) {
						console.log("Ready to generate ..!");
						console.info(res.data);
						//history.push("/generate", { petitionFields: res.data });
						history.push("/upload-preview", { petitionFields: res.data });
					}
				})
				.catch((err) => {
					console.error(err);
				});
		}
	}

	return (
		<div className='text-center'>
			<Modal.Dialog>
				<Modal.Header>
					<Modal.Title>Upload File</Modal.Title>
				</Modal.Header>

				<Modal.Body>
					<Col>
						<input
							type='file'
							name='docket_file'
							multiple
							accept='.pdf'
							onChange={(e) => {
								getFile(e.target.files);
							}}
						/>
						<ul style={{ listStyleType: "none" }}>{fileNameList}</ul>
					</Col>
				</Modal.Body>

				<Modal.Footer>
					<Button
						id='returnToLoginButton'
						variant='outline-secondary'
						onClick={returnToChooseAction}>
						Cancel
					</Button>
					<Button id='fileButton' onClick={chooseFile}>
						Submit
					</Button>
					{isError && <div>Please select a file</div>}
				</Modal.Footer>
			</Modal.Dialog>
		</div>
	);
}
