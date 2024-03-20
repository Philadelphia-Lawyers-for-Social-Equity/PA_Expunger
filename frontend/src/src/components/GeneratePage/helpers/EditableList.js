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

    function ShowLabel() {
        let result = "";
        if (!props.label)
            result = <></>;
        else if (props.isSubHeader)
            result = <div className='col-sm-2'><label className='form-label'><>{props.label}</></label></div>;
        else
            result = <h2>{props.label}</h2>;

        return result;
    }

    if (props.smallHeader) {
        return (
            <Form.Group as={Row}>
                <div className='col-sm-2'>
                    <label className='form-label'>
                        {props.label}
                    </label>
                </div>

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
                    <Col className="text-left">
                        <AddButton />
                    </Col>
                </Row>
            </Form.Group>
        );
    }
    else {
        return (
            <Form.Group as="div">
                {ShowLabel()}
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
}
