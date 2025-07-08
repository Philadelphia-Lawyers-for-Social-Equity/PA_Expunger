import React from 'react';
import { Route, Redirect, useLocation } from 'react-router-dom';
import { useAuth } from "./context/auth";

export default function PrivateRoute({ component: Component, ...rest }) {
    const { isAuthenticated } = useAuth();
    const location = useLocation();

    return (
        <Route
            {...rest}
            render={props => {
                if (isAuthenticated) {
                    return <Component {...props} />;
                } else {
                    return <Redirect to={`/login?next=${location.pathname}`} />;
                }
            }}
        />
    );
}
