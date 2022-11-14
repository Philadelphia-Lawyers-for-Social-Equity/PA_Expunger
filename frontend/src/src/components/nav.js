import React from "react";
import { Navbar, Nav } from "react-bootstrap";

const nav = () => (
  <Navbar 
    collapseOnSelect 
    expand="lg" 
    bg="light" 
    variant="light" 
    inverse="true" 
    fluid="true"
  >
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

{/* Sign up button is removed once user is logged in */}
        {localStorage.getItem("access_token") && <Nav.Link href="/signup">Sign up</Nav.Link>}
        {localStorage.getItem("access_token") && <Nav.Link href="/">Log in</Nav.Link>}
        {!localStorage.getItem("access_token") && <Nav.Link href="/profile">My profile</Nav.Link>}
        {!localStorage.getItem("access_token") && <Nav.Link href="/">Log out</Nav.Link>}
      </Nav>
    </Navbar.Collapse>
  </Navbar>
);

export default nav;
