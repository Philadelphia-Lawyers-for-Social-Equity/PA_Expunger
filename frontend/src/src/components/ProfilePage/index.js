import React, { useEffect, useState } from 'react';
// import { Redirect } from 'react-router-dom';
import "./style.css";
import axios from 'axios';
import { Button, Col, Modal, Row } from 'react-bootstrap';

export default function ProfilePage() {
  const [myUsername, setMyUsername] = useState("");
  const [myFirstName, setMyFirstName] = useState("");
  const [myLastName, setMyLastName] = useState("");
  const [myEmail, setMyEmail] = useState("");
  const [attorneypk, setAttorneypk] = useState(0);
  const [attorneyName, setAttorneyName] = useState("");
  const [attorneyBar, setAttorneyBar] = useState("");
  const [attorneyURL, setAttorneyURL] = useState("");
  const [orgpk, setOrgpk] = useState(0);
  const [addresspk, setAddresspk] = useState(0);
  const [orgName, setOrgName] = useState("");
  const [orgStreet, setOrgStreet] = useState("");
  const [orgCity, setOrgCity] = useState("");
  const [orgState, setOrgState] = useState("");
  const [orgZipcode, setOrgZipcode] = useState("");
  const [orgPhone, setOrgPhone] = useState("");
  const [orgURL, setOrgURL] = useState("");
  const [isEdit, setIsEdit] = useState(false);

  // useEffect is the React Hook equivalent to ComponentDidMount
  useEffect(() => {

    const bearer = "Bearer ";
    const token = bearer.concat(localStorage.getItem("access_token"));
    var config = {
      'headers': { 'Authorization': token }
    };

    // Get to return user data
    const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/my-profile/";
    axios.get(url, config)
      .then(
        res => {
          if (res.status === 200) {
            // return data
            setMyUsername(res.data.user.username);
            setMyFirstName(res.data.user.first_name);
            setMyLastName(res.data.user.last_name);
            setMyEmail(res.data.user.email);

            setAttorneypk(res.data.attorney.pk);
            setAttorneyName(res.data.attorney.name);
            setAttorneyBar(res.data.attorney.bar);
            setAttorneyURL(res.data.attorney.url);

            setOrgpk(res.data.organization.pk);
            setAddresspk(res.data.organization.address.pk);
            setOrgName(res.data.organization.name);
            setOrgStreet(res.data.organization.address.street1);
            setOrgCity(res.data.organization.address.city);
            setOrgState(res.data.organization.address.state);
            setOrgZipcode(res.data.organization.address.zipcode);
            setOrgPhone(res.data.organization.phone);
            setOrgURL(res.data.organization.url);
          }
        }
      )
  }, []); // empty array as the second argument will limit to one get call

  // onclick for Edit button
  function editProfile() {

    console.log("Edit button clicked");
    setIsEdit(true);

  }

  // PUT for profile editing
  function postProfile() {

    console.log("Submit button clicked");

    const sendData = {
      "attorney": {
        "bar": attorneyBar,
        "name": attorneyName,
        "pk": attorneypk,
        "url": attorneyURL
      },
      "organization": {
        "address": {
          "city": orgCity,
          "pk": addresspk,
          "state": orgState,
          "street1": orgStreet,
          "street2": null,
          "zipcode": orgZipcode
        },
        "name": orgName,
        "phone": orgPhone,
        "pk": orgpk,
        "url": orgURL
      },
      "user": {
        "email": myEmail,
        "first_name": myFirstName,
        "last_name": myLastName,
        "username": myUsername
      }
    }


    const shortData = {
      "attorney": attorneypk,
      "organization": orgpk,
      "user": {
        "email": myEmail,
        "first_name": myFirstName,
        "last_name": myLastName,
        "username": myUsername
      }
    }

    console.log(sendData);
    console.log(shortData);

    const bearer = "Bearer ";
    const token = bearer.concat(localStorage.getItem("access_token"));
    var config = {
      'headers': { 'Authorization': token }
    };

    const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/my-profile/";
    // axios.post(url, JSON.parse(postData), config)
    axios.put(url, shortData, config)
      .then(
        console.log("Posted")
      )
      .catch(err => {
        console.log(err);
      })

  }

  return (
    <div className="text-left">
      <Modal.Dialog>
        <Modal.Header closeButton>
          <Modal.Title>Profile Information</Modal.Title>
          <Button id="editbutton" onClick={editProfile}>Edit</Button>
        </Modal.Header>

        <Modal.Body>
          <Row>
            <Col>
              Username :
          </Col>
            <Col>
              {myUsername}
            </Col>
          </Row>
          <Row>
            <Col>
              Name :
          </Col>
            <Col>
              {!isEdit && myFirstName} {!isEdit && myLastName}
              {isEdit && <input type="text" onChange={e => {
                setMyFirstName(e.target.value);
              }} placeholder="First Name"  />}
              {isEdit && <input type="text" onChange={e => {
                setMyLastName(e.target.value);
              }} placeholder="Last Name"  />}
            </Col>
          </Row>
          <Row>
            <Col>
              Email Address :
          </Col>
            <Col>
              {!isEdit && myEmail}
              {isEdit && <input type="text" onChange={e => {
                setMyEmail(e.target.value);
              }} placeholder="Email"  />}
            </Col>
          </Row>
          <Row>
            <Col>
              Header Text for Petition :
          </Col>
            <Col>
              <p className="petp">{orgName}</p>
              <p className="petp">BY: {attorneyName}</p>
              <p className="petp">Identification no.:{attorneyBar} </p>
              <p className="petp"> </p>
              <p className="petp">{orgStreet}</p>
              <p className="petp">{orgCity}, {orgState} {orgZipcode}</p>
              <p className="petp">{orgPhone}</p>
            </Col>
          </Row>
          <Row>
            <Col>
              Expungement Petition Signature :
          </Col>
            <Col>
              {attorneyName}, Esquire
            </Col>
          </Row>
        </Modal.Body>

        <Modal.Footer>
          {isEdit && <Button id="submitButton" onClick={postProfile}>Submit</Button>}
        </Modal.Footer>

      </Modal.Dialog>
    </div>
  );
}
