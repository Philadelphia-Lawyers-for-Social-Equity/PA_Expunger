import React from "react";
//import { BrowserRouter as Link } from "react-router-dom";
import { Navbar, Nav } from "react-bootstrap";

const nav = () => (
  <Navbar collapseOnSelect expand="lg" bg="light" variant="light" inverse fluid>
    <Navbar.Brand href="/">
      <img
        src="http://plsephilly.org/wp-content/uploads/2014/11/PLSE_logotype_320.png"
        width="90"
        height="30"
        className="d-inline-block align-top"
        alt="PLSE logo"
      />
    </Navbar.Brand>
    <Navbar.Toggle aria-controls="basic-navbar-nav" />
    <Navbar.Collapse id="basic-navbar-nav">
      <Nav className="ml-auto">
        <Nav.Link href="/signup">
          Sign up
        </Nav.Link>

        {localStorage.getItem("access_token") && <Nav.Link href="/">Log in</Nav.Link>}

        {!localStorage.getItem("access_token") && <Nav.Link href="/">Log out</Nav.Link>}

      </Nav>
    </Navbar.Collapse>
  </Navbar>
);

export default nav;
