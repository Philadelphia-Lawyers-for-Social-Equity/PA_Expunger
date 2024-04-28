import React from "react";
import { useAuth } from "../../context/auth";
import { Button } from "react-bootstrap";

function Admin(props) {
  const { logout } = useAuth();

  return (
    <div>
      <div>Admin Page</div>
      <Button onClick={logout}>Log out</Button>
    </div>
  );
}

export default Admin;
