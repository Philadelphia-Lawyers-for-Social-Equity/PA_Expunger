import React, { useState } from "react";
import { Redirect } from 'react-router-dom';
import { Container, Row, Col, Form, Button } from "react-bootstrap";
import { useUser } from "../../context/user";

export default function SignUp() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [isProfileReady, setIsProfileReady] = useState(false);
  const [isError, setIsError] = useState(false);

  const { setUser } = useUser();

  // On click to check that all fields are entered
  function saveProfile() {

    if (firstName === "" || lastName === "" || email === "" || username === "" || password === "") {
      setIsError(true);
    }
    else {
      // store profile because we can't post without attorney info
      const currentUser = {
        firstName,
        lastName,
        email,
        username,
        role
      };
      setUser(currentUser);
      setIsProfileReady(true);
    }
  }

  if (isProfileReady) {
    return <Redirect to="/" />;
  }

  return (
    <Container>
      <Row>
        {" "}
        <h1>Sign up</h1>
      </Row>

      <Row>
        <Form>
          <Form.Row>
            <Col>
              <Form.Label>First name</Form.Label>
              <Form.Control value={firstName} onChange={e => {
                setFirstName(e.target.value);
              }} placeholder="First name" />
            </Col>
            <Col>
              <Form.Label>Last name</Form.Label>
              <Form.Control value={lastName} onChange={e => {
                setLastName(e.target.value);
              }} placeholder="Last name" />
            </Col>
          </Form.Row>

          <Form.Group controlId="formBasicRole">
            <Form.Label>Role</Form.Label>
            <Form.Control as="select" onChange={e => {
              setRole(e.target.value);
            }} custom>
              <option selected="true" disabled="disabled">Select...</option>
              <option value="Lawyer">Lawyer</option>
              <option value="Staff">Staff</option>
              <option value="Intern">Intern</option>
            </Form.Control>
          </Form.Group>

          <Form.Group controlId="formBasicEmail">
            <Form.Label>Email</Form.Label>
            <Form.Control type="email" value={email} onChange={e => {
              setEmail(e.target.value);
            }} placeholder="Enter email" />
          </Form.Group>

          <Form.Group controlId="formBasic">
            <Form.Label>Username</Form.Label>
            <Form.Control type="username" value={username} onChange={e => {
              setUsername(e.target.value);
            }} placeholder="Enter username" />
          </Form.Group>

          <Form.Group controlId="formBasicPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control type="password" value={password} onChange={e => {
              setPassword(e.target.value);
            }} placeholder="Password" />
          </Form.Group>

          <Button variant="primary" onClick={saveProfile}>Submit</Button>
          {isError && <div>Please fill missing information</div>}
        </Form>
      </Row>
    </Container>
  )
}
