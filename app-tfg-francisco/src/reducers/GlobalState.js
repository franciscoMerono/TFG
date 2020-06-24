import { ADD_AUTH } from "../actions/actions";
import Firebase from "../Firebase/Firebase";

const initialState = {
  encendido: false,
  authUser: null,
  firebase: new Firebase(),
};

function globalState(state = initialState, action) {
  if (action.type === ADD_AUTH){
      return Object.assign({}, state, {
        authUser: action.payload
      });
  }
  console.log(state)
  return state;
}

export default globalState;