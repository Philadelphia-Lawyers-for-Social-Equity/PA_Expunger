import React from "react";
import { Container } from "react-bootstrap";

export default function UploadSummary(props) {
	console.log(props);
	/*
        Will take in an array of petitions.
        Each petition will have an OTN
    */
	return (
		<div>
			<div>
				{props.petitions?.map((petition, i) => (
					<div className='row' key={i}>
						<div className='col-3'></div>
						<div className='col-3'>
							{" "}
							{petition.docket_info?.otn ?? "Unknown"}{" "}
						</div>
						<div className='col-3'>
							{" "}
							{petition.docket_numbers.map((num, i) => (
								<div>{num}</div>
							))}{" "}
						</div>
						<div className='col-3'></div>
					</div>
				))}
			</div>
			<div># of Petitions: {props.petitions?.length ?? 0}</div>
		</div>
	);
}
