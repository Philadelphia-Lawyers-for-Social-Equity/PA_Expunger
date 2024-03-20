import React from 'react';
import EditableList from '../helpers/EditableList';
import RemovableTextField from '../helpers/RemovableTextField';

export default function Dockets(props) {
    /* props expects:
        - dockets: a list of docket strings
        - handleChange: function should accept a list of docket strings and do the update
    */

    function makeItems() {
        return(props.dockets.map((d) => ({"text": d, "key": d})));
    }

    function saveItems(items) {
        let newDockets = items.map((item) => (item.text));
        props.handleChange(newDockets);
    }

    return (
        <EditableList
            label="Dockets"
            inner={RemovableTextField}
            items={makeItems()}
            emptyItem={{"text": "", "key": ""}}
            handleChange={(e) => {saveItems(e);}}
            disabled={props.disabled || false}
            smallHeader={false}
        />
    );
}
