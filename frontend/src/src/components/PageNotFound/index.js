import React, { useEffect } from 'react';
import { Modal } from 'react-bootstrap';

function PageNotFound() {
    useEffect(() => {
        document.body.style.backgroundColor = "var(--light-blue)";
    }, []);

    return (
        <Modal.Dialog>
            <Modal.Header>
                <Modal.Title>404: Page Not Found</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <p>The page you're looking for doesn't exist.</p>
                <p>Please check the URL or try navigating to a different page.</p>
            </Modal.Body>
        </Modal.Dialog>
    );
}

export default PageNotFound;
