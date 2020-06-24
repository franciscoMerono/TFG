import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { compose } from 'recompose';
import * as ROUTES from '../constants';
import { useSelector } from 'react-redux'
import Grid from '@material-ui/core/Grid';


const INITIAL_STATE = {
    email: '',
    password: '',
    error: null,
  };

const SignIn = (props) => {
    const firebase = useSelector(store => store.firebase);
    const auth = useSelector(store => store.authUser);
    const [state, setState] = useState( {...INITIAL_STATE} );
  
    const onSubmit = event => {
      const { email, password } = state;
      firebase
        .doSignInWithEmailAndPassword(email, password)
        .then(() => {          
          setState({ ...INITIAL_STATE });
          props.history.push(ROUTES.HOME);
        })
        .catch(error => {
          setState({ error });
        });
      event.preventDefault();
    };
  
    const onChange = event => {
      setState ({...state, [event.target.name]: event.target.value })
    };
    
  useEffect(() =>{
    if (auth) props.history.push(ROUTES.HOME);
  }, [auth, props.history])

    const isInvalid = state.password === '' || state.email === '';
      return (
        <div style={{display: "flex",
          justifyContent: "center",
          height: "100vh",
          paddingTop: "20%",
          background: "burlywood"}}>
        <form onSubmit={onSubmit} >   
        <Grid container spacing={2} style={{display:"inline-grid"}}>
          <input
            name="email"
            value={state.email}
            onChange={onChange}
            type="text"
            placeholder="Email Address"
          />
          <input
            name="password"
            value={state.password}
            onChange={onChange}
            type="password"
            placeholder="Password"
          />
          <button disabled={isInvalid} type="submit">
            Sign In
          </button>
          {state.error && <p>{state.error.message}</p>}
          </Grid>  
        </form>
        </div>
      );
  }
  
  const SignInForm = compose(
    withRouter,
  )(SignIn);
  
  export { SignInForm };