import React, { useRef, useEffect } from "react";
import GeneratorInput from "../helpers/GeneratorInput";
import Radio from "../helpers/Radio";
import { usePetitions } from "../../../context/petitions";

export default function Petition({ petitionNumber, disabled }) {
  /* props expects:
        - petitionNumber: integer
        - disabled: boolean
    */
  const { petitions, updatePetitions } = usePetitions();
  const docket_info = petitions[petitionNumber].docket_info;

  // store the original total of charges in a ref
  const totalChargesRef = useRef();
  useEffect(() => {
    if (totalChargesRef.current === undefined) {
      totalChargesRef.current = getCurrentTotalCharges();
    }
  }, [petitionNumber, petitions]);
  const totalCharges = totalChargesRef.current;

  // get the current total charges for the petition
  const getCurrentTotalCharges = () => petitions[petitionNumber].charges.length;

  // check whether current number of charges is less than the original amount
  const isPartialExpungement = () => totalCharges > getCurrentTotalCharges();

  function handleChange(changes) {
    updatePetitions("docket_info", petitionNumber, changes);
  }

  return (
    <>
      <h2>Petition</h2>
      <GeneratorInput
        label="Offense Tracking Number (OTN)"
        type="text"
        placeholder="########"
        name="otn"
        value={docket_info.otn}
        handleChange={handleChange}
        disabled={disabled || false}
      />
      <GeneratorInput
        label="Judge"
        type="text"
        placeholder="First & Last Name"
        name="judge"
        value={docket_info.judge}
        handleChange={handleChange}
        disabled={disabled || false}
      />
      <Radio
        label="Is this a full or partial expungement?"
        name="ratio"
        handleChange={handleChange}
        items={[
          ["full", "Full Expungement"],
          ["partial", "Partial Expungement"],
        ]}
        selected={
          (isPartialExpungement() && "partial") || docket_info.ratio || "full"
        }
        disabled={disabled || false}
      />
    </>
  );
}
