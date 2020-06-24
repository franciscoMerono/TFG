import globalState from './GlobalState'
import { createStore } from 'redux';

export const store = createStore(globalState);; 
    
