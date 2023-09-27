import React, { useState, useEffect, useRef } from "react";
import { Redirect } from "react-router-dom";
import axios from "axios";
import Alert from "react-bootstrap/Alert";
import { Button, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../../context/auth";

export default function LoginForm() {
  const [isError, setIsError] = useState(false);
  const [is404, setIs404] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const { authTokens, setAuthTokens } = useAuth();
  const isMounted = useRef(true);

  function onKeyUp(e) {
    if (e.key === 'Enter') {
      postLogin();
    }
  }

  function postLogin() {
    const url = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/auth/token/";
    console.debug("Login url: " + url);
    axios
      .post(url, {
        username: userName,
        password: password
      })
      .then(res => {
        if (isMounted.current) {
          if (res.status === 200) {
            setAuthTokens(res.data);
          } else {
            setIsError(true);
          }
        }
      })
      .catch(err => {
        if (isMounted.current) {
          console.error(err);
          setIsError(true);
        }
      });
  }

  useEffect(() => {
    if (authTokens && isMounted.current) {
      const profileurl = process.env.REACT_APP_BACKEND_HOST + "/api/v0.2.0/expunger/my-profile/";
      const token = `Bearer ${authTokens.access}`;

      var config = {
        'headers': { 'Authorization': token }
      };
  
      axios.get(profileurl, config)
        .then(
          res => {
            if (res.status === 200) {
              setHasProfile(true);
            }
          })      
          .catch(
            err => {
              if (err.response.status === 404) {
                setIs404(true);
              }
      });
    }
    return () => { isMounted.current  = false };
  }, [authTokens]);

  if (hasProfile || authTokens) {
    return <Redirect to="/" />;
  }

  if (is404) {
    return <Redirect to="/signup" />;
  }

  return (
    <div style={{width: "100%", height: "100vh", display: "flex", justifyContent: "center", alignItems: "center"}}>
      <Form style={{width: "50%"}}>
        <Form.Group as={Row}>
          <Form.Label column sm={2}>
            Username
          </Form.Label>
          <Col>
            <Form.Control
              type="text"
              id="username"
              name="username"
              placeholder="Username"
              value={userName}
              onChange={e => setUserName(e.target.value)}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row}>
          <Form.Label column sm={2}>
            Password
          </Form.Label>
          <Col>
            <Form.Control
              type="password"
              id="password"
              name="password"
              placeholder="Password"
              value={password}
              onKeyDown={e => onKeyUp(e)}
              onChange={e => setPassword(e.target.value)}
            />
          </Col>
        </Form.Group>
      <Form.Group as={Row}>
        <Col sm={{ offset: 2 }}>
          <Button
            id="SubmitButton"
            onClick={postLogin}
            name="action"
          >
            Submit
          </Button>
        </Col>
      </Form.Group>
      <Form.Group as={Row}>
        <Col>
          {isError && (
            <Alert variant="warning">The username or password provided were incorrect</Alert>
          )}
        </Col>
      </Form.Group>
      </Form>
    </div>
  );
}
