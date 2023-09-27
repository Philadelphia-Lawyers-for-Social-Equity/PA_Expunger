import React from "react";
import "./App.css";
import { BrowserRouter as Router, Route } from "react-router-dom"; // removed Switch
import PrivateRoute from "./PrivateRoute";
import { AuthProvider } from "./context/auth";
import { UserProvider } from "./context/user";
import LoginForm from "../src/components/LoginForm";
import ChooseAction from "../src/components/ChooseAction";
import SearchPage from "../src/components/SearchPage";
import LandingPage from "../src/components/LandingPage";
import FileUpload from "../src/components/FileUpload";
import GeneratePage from "./components/GeneratePage";
import ProfilePage from "../src/components/ProfilePage";
import BodyBackgroundColor from "react-body-backgroundcolor";
import SignUp from "./components/SignUp/signUp";
import Nav from "./components/nav";

function App(props) {
  return (
    <AuthProvider>
      <UserProvider>
        <Router>
          <Nav />
          <BodyBackgroundColor backgroundColor="#d9ecf9">
            <Route path="/login" render={props => <LoginForm {...props} isAuthed={true} />} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="#d9ecf9">
            <Route path="/signup" component={SignUp} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="gray">
            <PrivateRoute exact path="/" component={LandingPage} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="gray">
            <PrivateRoute path="/action" component={ChooseAction} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="#d9ecf9">
            <PrivateRoute path="/search" component={SearchPage} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="gray">
            <PrivateRoute path="/upload" component={FileUpload} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="#d9ecf9">
            <PrivateRoute path="/generate" component={GeneratePage} />
          </BodyBackgroundColor>

          <BodyBackgroundColor backgroundColor="#d9ecf9">
            <PrivateRoute path="/profile" component={ProfilePage} />
          </BodyBackgroundColor>
        </Router>
      </UserProvider>
    </AuthProvider>
  );
}

export default App;
