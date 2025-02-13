import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import PrivateRoute from "./PrivateRoute";
import { AuthProvider } from "./context/auth";
import { UserProvider } from "./context/user";
import { PetitionerProvider } from "./context/petitioner";
import LoginForm from "../src/components/LoginForm";
import ChooseAction from "../src/components/ChooseAction";
import SearchPage from "../src/components/SearchPage";
import LandingPage from "../src/components/LandingPage";
import FileUpload from "../src/components/FileUpload";
import GeneratePage from "./components/GeneratePage";
import ProfilePage from "../src/components/ProfilePage";
import ReviewPage from "./components/ReviewPage";
// import SignUp from "./components/SignUp/signUp";
import Nav from "./components/nav";
import PageNotFound from "./components/PageNotFound";
import { PetitionsProvider } from "./context/petitions";

function App(props) {
  return (
    <PetitionerProvider>
      <PetitionsProvider>
        <AuthProvider>
          <UserProvider>
            <Router>
              <Nav />
              <Switch>
                <Route exact path="/login" render={props => <LoginForm {...props} isAuthed={true} />} />
                {/* <Route exact path="/signup" component={SignUp} /> */}
                <PrivateRoute exact path="/" component={LandingPage} />
                <PrivateRoute exact path="/action" component={ChooseAction} />
                <PrivateRoute exact path="/search" component={SearchPage} />
                <PrivateRoute exact path="/profile" component={ProfilePage} />
                  <PrivateRoute exact path="/upload" component={FileUpload} />
                  <PrivateRoute exact path="/generate" component={GeneratePage} />
                  <PrivateRoute exact path ="/review" component={ReviewPage}/>
                <PrivateRoute path="*" component={PageNotFound} />
              </Switch>
            </Router>
          </UserProvider>
        </AuthProvider>
      </PetitionsProvider>
    </PetitionerProvider>
  );
}

export default App;
