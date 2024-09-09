import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import { useAuth } from '../context/auth';
import { usePetitioner, initialPetitionerState } from '../context/petitioner';

const Navigation = () => {
  const { logout, authTokens } = useAuth();
  const { setPetitioner } = usePetitioner();

  const logOutAndReset = () => {
    setPetitioner(initialPetitionerState);
    logout();
  }

  return (
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
          {authTokens ? (
            <>
              <Nav.Link as={Link} to="/profile">Profile</Nav.Link>
              <Nav.Link onClick={logOutAndReset}>Log out</Nav.Link>
            </>
          ) : (
            <>
              <Nav.Link href="/signup">Sign up</Nav.Link>
              <Nav.Link href="/login">Log in</Nav.Link>
            </>
          )}
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

export default Navigation;
