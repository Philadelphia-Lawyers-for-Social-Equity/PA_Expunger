import React, { useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';
import { v4 as uuidv4 } from 'uuid';

export default function EditableList(props) {
    /* Turn a list of property objects into specified items, including widgets
       to add or remove extra items

        props expects:
            - label
            - inner: the Inner component to attach to each property.  Should
              accept a "key" argument or provide its own index.
            - emptyItem: property object template for a new item
            - items: array of property objects appropriate for Inner component
            - handleChange
    */

    const Inner = props.inner;
    const [showAddButton, setShowAddButton] = useState(true);

    function addItem() {
        let arr = props.items.slice();
        arr.push(props.emptyItem);
        props.handleChange(arr);
    }

    function updateItem(idx, newItem) {
        let arr = props.items.slice();
        arr.splice(idx, 1, newItem);
        props.handleChange(arr);
    }

    function dropItem(idx) {
        let arr = props.items.slice();
        arr.splice(idx, 1);
        console.log("Dropped item: " + idx);
        props.handleChange(arr);
    }

    function isEmpty(obj) {
        let objString = JSON.stringify(obj);
        let emptyString = JSON.stringify(props.emptyItem);
        return(objString == emptyString);
    }

    function AddButton() {
        let variant = "primary";
        let onClick = () => {addItem()};

        if (props.items.length > 0 && isEmpty(props.items.slice(-1)[0])) {
            variant = "secondary"
            onClick = null;
        }
        return(
            <Button
                variant={variant}
                onClick={onClick}
            >Add { props.label }</Button>
        );
    }

    return (
        <Form.Group as="div">
            { props.label ? <h2>{props.label}</h2> : <></> }
            { props.items.map((innerProps, idx) => {
                    return(
                        <Inner
                            {...innerProps}
                            key={uuidv4()}
                            handleChange={(txt) => {updateItem(idx, txt);}}
                            handleRemove={() => { dropItem(idx);}}
                />);
            })}

            <Row>
                <Col sm={2}/>
                <Col className="text-left" sm={8}>
                    <AddButton />
                </Col>
            </Row>
        </Form.Group>
    );

}