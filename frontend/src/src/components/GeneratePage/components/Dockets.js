import React from 'react';
import EditableList from '../helpers/EditableList';

export default function Dockets(props) {
    /* props expects:
        - dockets: a list of docket strings
        - handleChange: function should accept a list of docket strings and do the update
    */

    const [dockets, setDockets] = useState(props.dockets);

    function makeItems() {
        return(dockets.map((d) => ({"text": d, "key": d})));
    }

    function saveItems(items) {
        let newDockets = items.map((item) => (item.text));
        setDockets(newDockets);
    }

    function save(){
        props.handleChange(dockets);
    }

    useEffect(() => {save();}, [dockets]);

    return (
        <EditableList
            label="Dockets"
            inner={RemovableTextField}
            items={makeItems()}
            emptyItem={{"text": "", "key": ""}}
            handleChange={(e) => {saveItems(e);}}
        />
    );
}
