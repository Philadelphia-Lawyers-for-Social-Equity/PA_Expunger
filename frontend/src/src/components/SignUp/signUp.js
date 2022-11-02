import React, { useState } from "react";
import { Redirect } from "react-router-dom";
import { Container, Row, Col, Form, Button } from "react-bootstrap";
import axios from "axios";

export default function SignUp() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isProfileReady, setIsProfileReady] = useState(false);
  const [isError, setIsError] = useState(false);

  // On click to check that all fields are entered
  async function saveProfile() {
    // check that
    if (
      firstName === "" ||
      lastName === "" ||
      role === "" ||
      email === "" ||
      username === "" ||
      password === ""
    ) {
      setIsError(true);
    } else {
      // store profile because we can't post without attorney info
      localStorage.setItem("firstName", firstName);
      localStorage.setItem("lastName", lastName);
      localStorage.setItem("role", role);
      localStorage.setItem("email", email);
      localStorage.setItem("username", username);
      localStorage.setItem("password", password);

      const profileURL =
        process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/my-profile/";
      const bearer = "Bearer ";
      const token = bearer.concat(localStorage.getItem("access_token"));
      const config = {
        headers: { Authorization: token },
      };

      const profileData = {
        firstName,
        lastName,
        role,
        email,
        username,
        password,
      };
      await axios.post(profileURL, { user: profileData }, config).catch((err) => {
        console.error(err);
      });
      setIsProfileReady(true);
    }
  }

  if (isProfileReady) {
    return <Redirect to="/landing" />;
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
              <Form.Control
                value={firstName}
                onChange={(e) => {
                  setFirstName(e.target.value);
                }}
                placeholder="First name"
              />
            </Col>
            <Col>
              <Form.Label>Last name</Form.Label>
              <Form.Control
                value={lastName}
                onChange={(e) => {
                  setLastName(e.target.value);
                }}
                placeholder="Last name"
              />
            </Col>
          </Form.Row>

          <Form.Group controlId="role">
            <Form.Label>Role</Form.Label>
            <Form.Control
              as="select"
              type="role"
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
              }}
              placeholder="Role"
            >
              <option>Lawyer</option>
              <option>Staff</option>
              <option>Intern</option>
            </Form.Control>
          </Form.Group>

          <Form.Group controlId="formBasicEmail">
            <Form.Label>Email</Form.Label>
            <Form.Control
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              placeholder="Enter email"
            />
          </Form.Group>

          <Form.Group controlId="formBasic">
            <Form.Label>Username</Form.Label>
            <Form.Control
              type="username"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
              }}
              placeholder="Enter username"
            />
          </Form.Group>

          <Form.Group controlId="formBasicPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
              }}
              placeholder="Password"
            />
          </Form.Group>

          <Button
            variant="primary"
            onClick={saveProfile}
            style={{ marginBottom: `60px` }}
          >
            Submit
          </Button>
          {isError && <div>Please fill missing information</div>}
        </Form>
      </Row>
    </Container>
  );
}
