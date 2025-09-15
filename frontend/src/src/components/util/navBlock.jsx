import React, { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { useAuth } from '../../context/auth';

/**
 * Renders no UI. Attaches event listeners to block navigation when active.
 * This component is intended to be placed on pages with forms or unsaved data.
 * @param {{ blockNav: React.MutableRefObject<boolean> }} props
 */
export default function NavBlock({blockNav}) {
    const history = useHistory();
    const { isAuthenticated } = useAuth();

    // If the user tries to reload or close the page, pop up a confirmation dialog
    useEffect(() => {
        const handleBeforeUnload = (event) => {
            if (blockNav.current && isAuthenticated) {
                event.preventDefault();
                event.returnValue = '';
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => window.removeEventListener('beforeunload', handleBeforeUnload)
    }, [blockNav, isAuthenticated])

    // If the user tries to navigate away from a page where data could be lost using React Router, pop up a confirmation dialog
    useEffect(() => {
        const unblock = history.block((destination) => {
            if (blockNav.current && isAuthenticated) {
                // It's safe to navigate between these paths
                const safePaths = ['/upload', '/generate', '/review'];
                if (!safePaths.includes(destination.pathname)) {
                    return window.confirm('Changes to petitions may not be saved. Are you sure you want to leave?');
                }
            }
            return true;
        });

        return () => unblock();
    }, [blockNav, history, isAuthenticated])

    return <></>;
}
