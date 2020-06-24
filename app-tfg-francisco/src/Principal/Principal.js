import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux';
import { withRouter } from 'react-router-dom';
import { compose } from 'redux';
import * as ROUTES from '../constants';
import PowerSettingsNewIcon from '@material-ui/icons/PowerSettingsNew';
import { IgrRadialGauge } from 'igniteui-react-gauges';

const Principal = (props) => {
    const [encendido, setEncendido] = useState()
    const firebase = useSelector(store => store.firebase);
    const authUser = useSelector(store => store.authUser);
    const [velocidad, setVelocidad] = useState(0)
    const [distancia, setDistancia] = useState(0)
  useEffect(() => {
    if (!authUser) props.history.push(ROUTES.SIGN_IN)
    firebase.encendido().on('value', snapshot => {
      setEncendido(snapshot.node_.value_);
    });
    firebase.velocidad().on('value', snapshot => {
      setVelocidad(snapshot.node_.value_);
    });
    firebase.distancia().on('value', snapshot => {
      setDistancia(snapshot.node_.value_/100);
    });
    return () => {
      firebase.encendido().off();
      firebase.velocidad().off();
      firebase.distancia().off();
    }
  }, [authUser, firebase, props.history])
 
  return(
    encendido===true ? (
    <div style={{background: "burlywood", height: "100%" , textAlignLast: "end"}}>
    <button onClick={e => { firebase.doSignOut()}}>SingOut</button>
    <div style={{display: "flex",
    justifyContent: "center",
    paddingTop: "10%",
    }}>
      <header >
        <div style={{textAlignLast: "center"}}>
        <PowerSettingsNewIcon style={{color:"red", fontSize: "xxx-large"}} onClick={() => {firebase.setEncendido(!encendido)}}/>

          <div>
            <h1>Robot encendido</h1>
            <hr/>
            <h1>Velocidadkm/h</h1>
            <IgrRadialGauge
              backingShape="Fitted"
              backingBrush="#A1FED2"
              backingOversweep={5}
              backingCornerRadius={10}
              backingStrokeThickness={5}
              backingOuterExtent={0.8}
              backingInnerExtent={0.15}
              scaleStartAngle={135} scaleEndAngle={45}
              height="300px"
              minimumValue={0} value={velocidad}
              maximumValue={30} interval={5}/>
            <hr/>
            <h1>{distancia} metros recorridos</h1>
          </div>
          </div>
      </header>
    </div>
    </div>
        ): (
          <div style={{background: "burlywood", height: "100vh" , textAlignLast: "end"}}>
    <button onClick={e => { firebase.doSignOut()}}>SingOut</button>
    <div style={{display: "flex",
    justifyContent: "center",
    paddingTop: "10%",
    }}>
      <header >
        <div style={{textAlignLast: "center"}}>
        <PowerSettingsNewIcon style={{color:"red", fontSize: "xxx-large"}} onClick={() => {firebase.setEncendido(!encendido)}}/>

          <h1>Robot apagado</h1>
                
        </div>
      </header>
    </div>
    </div>
        )
  )
}

const PrincipalPage = compose(
    withRouter,
  )(Principal);
  
  export { PrincipalPage };
