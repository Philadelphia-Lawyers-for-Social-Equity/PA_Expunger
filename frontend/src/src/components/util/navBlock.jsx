import React, { useEffect } from 'react';
import { useHistory } from 'react-router-dom';

export default function NavBlock({blockNav}) {
    const history = useHistory();

    // If the user tries to reload the page, pop up a confirmation dialog
    useEffect(() => {
        const handleBeforeUnload = (event) => {
            if (blockNav.current) {
                event.preventDefault();
                event.returnValue = '';
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => window.removeEventListener('beforeunload', handleBeforeUnload)
    }, [blockNav, history])

    // If the user tries to navigate from the /generate page to another page, pop up a confirmation dialog
    useEffect(() => {
        const unblock = history.block((location, action) => {
            // console.log("location: ", location)
            // console.log("action: ", action)
            if (blockNav.current) {
                if (location.pathname !== "/generate") {
                    // console.log("action 2: ", action)
                    return window.confirm('Changes to petitions may not be saved. Are you sure you want to leave?');
                }
            }
            return true;
        });

        return () => unblock();
    }, [blockNav, history])

    return <></>;
}
