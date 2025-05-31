import React, {useEffect, useState} from "react";
import {Redirect} from "react-router-dom";
import api from "../../services/api"
import Alert from "react-bootstrap/Alert";
import {Button, Form} from "react-bootstrap";
import {LOGOUT_REASON_KEY, useAuth} from "../../context/auth";
import {useIsMounted} from "../../hooks/useIsMounted";

export default function LoginForm() {
    const [isLoggingIn, setIsLoggingIn] = useState(false);
    const [loginError, setLoginError] = useState("");
    const [userName, setUserName] = useState("");
    const [password, setPassword] = useState("");
    const [logoutMessage, setLogoutMessage] = useState("");

    const {isAuthenticated, setAuthTokens} = useAuth();
    const getIsMounted = useIsMounted();

    // Check for logout reason message
    useEffect(() => {
        const reason = sessionStorage.getItem(LOGOUT_REASON_KEY);
        if (reason) {
            if (getIsMounted()) {
                setLogoutMessage(reason);
            }
            sessionStorage.removeItem(LOGOUT_REASON_KEY); // Clear after displaying once
        }
    }, [getIsMounted]);

    const handleLoginSubmit = async (event) => {
        // Prevent default form submission
        if (event && typeof event.preventDefault === 'function') {
            event.preventDefault();
        }

        if (getIsMounted()) {
            setIsLoggingIn(true);
            setLoginError("");
            setLogoutMessage("");
        } else {
            return;
        }

        try {
            const tokens = await api.login(userName, password);
            if (getIsMounted()) {
                setAuthTokens(tokens);
            }
        } catch (error) {
            if (getIsMounted()) {
                setLoginError(error.response?.data?.detail || error.message ||
                    "Login failed. Please check your credentials.");
            }
        } finally {
            if (getIsMounted()) {
                setIsLoggingIn(false);
            }
        }
    };

    if (isAuthenticated) {
        return <Redirect to="/"/>;
    }

    return (
        <div
            style={{
                width: "100%",
                height: "100vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
            }}>
            <Form style={{width: "100%", maxWidth: "25em"}} onSubmit={handleLoginSubmit}>
                <h2 className="text-center mb-4">Login</h2>
                {logoutMessage && (
                    <Alert variant="info" onClose={() => setLogoutMessage("")} dismissible className="mb-3">
                        {logoutMessage}
                    </Alert>
                )}
                <Form.Group className="mb-1">
                    <Form.Label>Username</Form.Label>
                    <Form.Control
                        type="text"
                        id="username"
                        name="username"
                        placeholder="Username"
                        value={userName}
                        onChange={(e) => setUserName(e.target.value)}
                        disabled={isLoggingIn}
                    />
                </Form.Group>
                <Form.Group className="mb-4">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                        type="password"
                        id="password"
                        name="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={isLoggingIn}
                    />
                </Form.Group>
                <Form.Group>
                    <Button
                        id="SubmitButton"
                        type="submit"
                        disabled={isLoggingIn || !userName || !password}
                        // onClick={handleLoginSubmit}
                        name="action"
                        className="w-100"
                    >
                        {isLoggingIn ? "Logging in..." : "Submit"}
                    </Button>
                </Form.Group>
                {loginError && (
                    <Alert variant="danger" className="mt-3" onClose={() => setLoginError("")} dismissible>
                        {loginError}
                    </Alert>
                )}
            </Form>
        </div>
    );
}
