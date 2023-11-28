import React from "react";
import GeneratorInput from "../helpers/GeneratorInput";
import EditableList from "../helpers/EditableList";
import Address from "../helpers/Address";
import RemovableTextField from "../helpers/RemovableTextField";

export default function Petitioner(props) {
  /* Props expects:
        - name: string
        - aliases: array of strings
        - dob: iso formatted date string
        - handleChange: function to handle updates

        We don't currently take the address or ssn as arguments because they are
        not available is any of our source data.  Manual entry only.

        Side effects
        - adds address via handleChange
    */

  function aliasItems() {
    if (!props.aliases) {
      return [];
    }

    return props.aliases.map((a) => ({ text: a, key: a }));
  }

  function saveAliases(items) {
    let newAliases = items.map((a) => a.text);
    props.handleChange({ aliases: newAliases });
  }

<<<<<<< Updated upstream
  function updateSsn(e) {
    if (props.ssn === undefined) {
      props.handleChange({ ssn: e.ssn });
      return;
    }
    let ssn = e.ssn;

    if (ssn.length > 11) {
      return;
    }

    if (ssn.length === 3 || ssn.length === 6) {
      ssn += "-";
    }
    props.handleChange({ ssn: ssn });
  }

  return (
    <>
      <h2>Petitioner</h2>
      <GeneratorInput
        label="Full Name"
        type="text"
        placeholder="Full Name"
        name="name"
        value={props.name}
        handleChange={props.handleChange}
        required={true}
      />

      <GeneratorInput
        label="Birth Date"
        type="date"
        name="dob"
        value={props.dob}
=======
  function formatSsn(value) {
    if (!value) return value;

    const ssn = value.replace(/[^\d]/g, "");

    const ssnLength = ssn.length;

    if (ssnLength < 4) return ssn;

    if (ssnLength < 6) {
      return `${ssn.slice(0, 3)}-${ssn.slice(3)}`;
    }

    return `${ssn.slice(0, 3)}-${ssn.slice(3, 5)}-${ssn.slice(5, 9)}`;
  }

  function handleSsnInput(res) {
    const formattedSsn = formatSsn(res["ssn"]);
    props.handleChange({ ssn: formattedSsn });
  }

  return (
    <>
      <h2>Petitioner</h2>
      <GeneratorInput
        label="Full Name"
        type="text"
        placeholder="Full Name"
        name="name"
        value={props.name}
>>>>>>> Stashed changes
        handleChange={props.handleChange}
        required={true}
      />

      <GeneratorInput
<<<<<<< Updated upstream
        label="Social Security Number"
        type="text"
        placeholder="###-##-####"
        name="ssn"
        value={props.ssn}
        handleChange={updateSsn}
        required={true}
      />

=======
        label="Birth Date"
        type="date"
        name="dob"
        value={props.dob}
        handleChange={props.handleChange}
        required={true}
      />

      <GeneratorInput
        label="Social Security Number"
        type="text"
        placeholder="###-##-####"
        name="ssn"
        value={props.ssn}
        handleChange={handleSsnInput}
        required={true}
      />

>>>>>>> Stashed changes
      <EditableList
        label="Aliases"
        inner={RemovableTextField}
        emptyItem={{ text: "", key: "" }}
        items={aliasItems()}
        handleChange={(e) => {
          saveAliases(e);
        }}
      />

      <Address
        {...props.address}
        handleChange={(a) => {
          props.handleChange({ address: a });
        }}
      />
    </>
  );
}
