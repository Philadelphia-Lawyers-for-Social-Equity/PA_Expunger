import React from 'react';
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
            - smallHeader: should the header be in a small font?
    */

    const Inner = props.inner;

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
        return(objString === emptyString);
    }

    function showLabel() {
        if (props.smallHeader) {
            return <Form.Label>{props.label}</Form.Label>;
        } else if (!props.label) {
            return <></>;
        } else {
            return <h2>{props.label}</h2>;
        }
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
                disabled={props.disabled || false}
            >Add { props.label }</Button>
        );
    }

    return (
        <Form.Group as="div">
            {showLabel()}
            { !props.items.length && (
                <span style={{color: '#dc3545'}}>
                    <svg xmlns="http://www.w3.org/2000/svg" strokeWidth="20" width="16" height="16" fill="currentColor" className="bi bi-exclamation-circle" viewBox="0 0 16 16">
                        <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                        <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>
                    </svg>
                    {'  '}At least one {props.label.slice(0, props.label.length - 1).toLowerCase()} is required
                </span>
            )}
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
