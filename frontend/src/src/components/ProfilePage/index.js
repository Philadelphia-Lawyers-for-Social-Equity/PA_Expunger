import React, { useEffect, useState } from 'react';
// import { Redirect } from 'react-router-dom';
import "./style.css";
import { Button, Col, Modal, Row } from 'react-bootstrap';
import { useAuth } from "../../context/auth";
import { useUser } from '../../context/user';

export default function ProfilePage() {
  const { user } = useUser();
  const [myUsername, setMyUsername] = useState(user.username);
  const [myFirstName, setMyFirstName] = useState(user.firstName);
  const [myLastName, setMyLastName] = useState(user.lastName);
  const [myEmail, setMyEmail] = useState(user.email);
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
  const { authedAxios } = useAuth();

  // useEffect is the React Hook equivalent to ComponentDidMount
  useEffect(() => {

    // Get to return user data
    const url = '/expunger/my-profile/';
    authedAxios.get(url)
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
  }, [authedAxios]); // empty array as the second argument will limit to one get call

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

    const url = '/expunger/my-profile/';
    // axios.post(url, JSON.parse(postData), config)
    authedAxios.put(url, shortData)
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
              {isEdit && <input type="text" value={myFirstName} onChange={e => {
                setMyFirstName(e.target.value);
              }} placeholder="First Name" />}
              {isEdit && <input type="text" value={myLastName} onChange={e => {
                setMyLastName(e.target.value);
              }} placeholder="Last Name" />}
            </Col>
          </Row>
          <Row>
            <Col>
              Email Address :
            </Col>
            <Col>
              {!isEdit && myEmail}
              {isEdit && <input type="text" value={myEmail} onChange={e => {
                setMyEmail(e.target.value);
              }} placeholder="Email" />}
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
