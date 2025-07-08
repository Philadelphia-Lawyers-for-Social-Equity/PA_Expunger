import {Card} from 'react-bootstrap';

export default function FallbackMessage(props) {
    const message = props.message || "If you see this message for more than a few seconds, please click on the home button (top left) and try again.";
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            padding: '20px'
        }}>
            <Card style={{maxWidth: '500px', width: '100%'}} className="text-center shadow">
                <Card.Body>
                    <Card.Text>
                        {message}
                    </Card.Text>
                </Card.Body>
            </Card>
        </div>)
}
