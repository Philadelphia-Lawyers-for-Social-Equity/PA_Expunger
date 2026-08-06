import React, { useEffect } from 'react';
import { useHistory } from 'react-router-dom';

/**
 * Renders no UI. Attaches event listeners to block navigation when active.
 * This component is intended to be placed on pages with forms or unsaved data.
 * @param {{ blockNav: React.MutableRefObject<boolean> }} props
 */
export default function NavBlock({blockNav}) {
    const history = useHistory();

    // If the user tries to reload or close the page, pop up a confirmation dialog
    useEffect(() => {
        const handleBeforeUnload = (event) => {
            if (blockNav.current) {
                event.preventDefault();
                event.returnValue = '';
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => window.removeEventListener('beforeunload', handleBeforeUnload)
    }, [blockNav])

    // If the user tries to navigate away from a page where data could be lost using React Router, pop up a confirmation dialog
    useEffect(() => {
        const unblock = history.block((destination) => {
            // Only ask about departures the user could decide differently. Losing the
            // session redirects here with the work already gone, and a deliberate logout
            // clears blockNav before it navigates, so nobody reaches the login page with
            // a choice left to make.
            if (destination.pathname === '/login') {
                return true;
            }
            if (blockNav.current) {
                // It's safe to navigate between these paths
                const safePaths = ['/upload', '/generate', '/review'];
                if (!safePaths.includes(destination.pathname)) {
                    return window.confirm('Changes to petitions may not be saved. Are you sure you want to leave?');
                }
            }
            return true;
        });

        return () => unblock();
    }, [blockNav, history])

    return <></>;
}
