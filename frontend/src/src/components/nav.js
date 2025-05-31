import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import { useAuth } from '../context/auth';
import { usePetitioner, initialPetitionerState } from '../context/petitioner';
import { usePetitions, initialPetitionState } from '../context/petitions';

const Navigation = () => {
  const { logout, isAuthenticated } = useAuth();
  const { setPetitioner } = usePetitioner();
  const { setPetitions } = usePetitions();

  const logOutAndReset = () => {
    setPetitioner(initialPetitionerState);
    setPetitions(initialPetitionState);
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
      <Navbar.Brand as={Link} to="/">
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
          {isAuthenticated ? (
            <>
              {/*<Nav.Link as={Link} to="/profile">Profile</Nav.Link>*/}
              <Nav.Link onClick={logOutAndReset}>Log out</Nav.Link>
            </>
          ) : (
            <>
              {/* <Nav.Link href="/signup">Sign up</Nav.Link> */}
              <Nav.Link href="/login">Log in</Nav.Link>
            </>
          )}
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

export default Navigation;
