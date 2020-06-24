import React, { useEffect, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import * as ROUTES from './constants';
import { SignInForm } from './SignIn/SignIn';
import { PrincipalPage } from './Principal/Principal';
import { addAuth } from './actions/actions';
import { CircularProgress } from '@material-ui/core';

const App = () => {
    const firebase = useSelector(store => store.firebase);
    const loading = useSelector(store => store.loading);
    const dispatch = useDispatch()
    useEffect(() => {
      firebase.auth.onAuthStateChanged(authUser => {
        authUser
          ? dispatch(addAuth(authUser))
          : dispatch(addAuth(null))
      })
    })
    
    return (
        loading ?
        (<CircularProgress />):
        (
              <Router>
                  <Switch>
                      <Route path={ROUTES.SIGN_IN} component={SignInForm} />
                      <Route path={ROUTES.HOME} component={PrincipalPage} />
                      <Route path="*" component={SignInForm} />
                  </Switch>
              </Router>  
        )
      )
    }

export default App;
