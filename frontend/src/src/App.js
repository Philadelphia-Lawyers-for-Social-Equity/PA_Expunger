import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
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
// TODO: Remove code related to BodyBackgroundColor before submitting PR.
//  See Issue #161, "[Feature Request] 404 Page."

// import BodyBackgroundColor from "react-body-backgroundcolor";
import SignUp from "./components/SignUp/signUp";
import Nav from "./components/nav";
import PageNotFound from "./components/PageNotFound";

function App(props) {
  return (
    <AuthProvider>
      <UserProvider>
        <Router>
          <Nav />
          <Switch>
            <Route path="/login" render={props => <LoginForm {...props} isAuthed={true} />} />
            <Route path="/signup" component={SignUp} />

            {/* <BodyBackgroundColor backgroundColor="gray"> */}
            <PrivateRoute exact path="/" component={LandingPage} />
            {/* </BodyBackgroundColor> */}

            {/* <BodyBackgroundColor backgroundColor="gray"> */}
            <PrivateRoute path="/action" component={ChooseAction} />
            {/* </BodyBackgroundColor> */}

            <PrivateRoute path="/search" component={SearchPage} />

            {/* <BodyBackgroundColor backgroundColor="gray"> */}
            <PrivateRoute path="/upload" component={FileUpload} />
            {/* </BodyBackgroundColor> */}

            <PrivateRoute path="/generate" component={GeneratePage} />
            <PrivateRoute path="/profile" component={ProfilePage} />
            <PrivateRoute path="*" component={PageNotFound} />
          </Switch>
        </Router>
      </UserProvider>
    </AuthProvider>
  );
}

export default App;
