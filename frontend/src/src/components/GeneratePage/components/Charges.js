import React from 'react';
import EditableList from '../helpers/EditableList';

export default function Charges(props) {
    /* props expects:
        - charges: list of charge objects, per the api glossary or Charge props
        - handleChange: function should take a list of charge objects, handle the update
    */

    const [charges, setCharges] = useState(props.charges);

    function makeItems() {
        return(charges.map((c, i) => ({...c, "key": i})));
    }

    function saveItems(items) {
        items.map((obj) => {delete obj.key;});
        setCharges(items);
    }

    function save() { props.handleChange(charges); }

    useEffect(() => {save()}, [charges]);

    return (
        <EditableList
            label="Charges"
            inner={RemovableCharge}
            items={makeItems()}
            emptyItem={{"statute": "", "description": "", "grade": "", "date": "", "disposition": "", "key": ""}}
            handleChange={(e) => {saveItems(e);}}
        />
    );
}
