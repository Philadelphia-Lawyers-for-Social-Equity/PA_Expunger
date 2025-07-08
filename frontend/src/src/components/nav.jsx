import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
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
    logout("You have successfully logged out.");
  }

  return (
    <Navbar
      collapseOnSelect
      expand="lg"
      bg="light"
      variant="light"
      inverse="true"
      sticky="top"
    >
      <Container fluid>
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
          <Nav className="ms-auto">
            {isAuthenticated ? (
              <>
                {/*<Nav.Link href="/profile">Profile</Nav.Link>*/}
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
      </Container>
    </Navbar>
  );
};

export default Navigation;
