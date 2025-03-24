import React, { useEffect } from 'react';
//import { useHistory } from 'react-router-dom';
import { useAuth } from '../context/auth';
import { usePetitioner, initialPetitionerState } from '../context/petitioner';

const Logout = (props) => {
  const { logout } = useAuth();
  const { setPetitioner } = usePetitioner();

  //const history = useHistory();
    
    useEffect( () => {
        props.setShouldBlockNavigation(false);
        setPetitioner(initialPetitionerState);
        logout();
        //history.push('/');
    });

    return (
        <div>You have been successfully logged out</div>
    );
}

export default Logout;
