import React from "react";
import { BsCheckSquareFill, BsFillSquareFill, BsSquareFill } from "react-icons/bs";


export default function Progress({petitionNumber, totalPetitions}) {

    const progressBar = Array(totalPetitions).fill(0).map((_, index) => {
        if (index > petitionNumber) {
            return (
                <span key={index} className="mr-2 text-white">
                    <BsSquareFill />
                </span>
            )   
        } else if (index === petitionNumber) {
            return (
                <span key={index} className="mr-2 text-primary">
                    <BsFillSquareFill />
                </span>
            )
        } else {
            return (
                <span key={index} className="mr-2 text-success">
                    <BsCheckSquareFill />
                </span>
            )
        }
    });

    return (
        <div className="d-flex flex-row" >
            <div className="mt-2 mr-2">
                Petition {petitionNumber + 1} of {totalPetitions}
            </div>
            <div className="mt-2">
                {progressBar}
            </div>
        </div>
    )
}