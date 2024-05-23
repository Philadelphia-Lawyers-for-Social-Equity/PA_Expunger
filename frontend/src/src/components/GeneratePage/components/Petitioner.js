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

	return (
		<>
			<h2>Petitioner</h2>
			<GeneratorInput
				label='Defendant Name'
				type='text'
				placeholder='Defendant Name'
				name='name'
				value={props.name}
				handleChange={props.handleChange}
				required={true}
				disabled={props.disabled || false}
			/>

			<GeneratorInput
				label='Petitioner Name'
				type='text'
				placeholder='Petitioner Name'
				name='petitionerName'
				value={props.petitionerName}
				handleChange={props.handleChange}
				required={true}
				disabled={props.disabled || false}
			/>

			<GeneratorInput
				label='Birth Date'
				type='date'
				name='dob'
				value={props.dob}
				handleChange={props.handleChange}
				required={true}
				disabled={props.disabled || false}
			/>

			<GeneratorInput
				label='Social Security Number'
				type='text'
				placeholder='###-##-####'
				name='ssn'
				value={props.ssn}
				handleChange={props.handleChange}
				required={true}
				disabled={props.disabled || false}
			/>

			<EditableList
				label='Aliases'
				inner={RemovableTextField}
				emptyItem={{ text: "", key: "" }}
				items={aliasItems()}
				handleChange={(e) => {
					saveAliases(e);
				}}
				disabled={props.disabled || false}
				smallHeader={true}
			/>

			<Address
				{...props.address}
				handleChange={(a) => {
					props.handleChange({ address: a });
				}}
				disabled={props.disabled || false}
			/>
		</>
	);
}
