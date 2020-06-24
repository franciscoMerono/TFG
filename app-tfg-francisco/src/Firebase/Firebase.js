import app from 'firebase/app';
import 'firebase/auth';
import 'firebase/database';
const config = {
  apiKey: process.env.REACT_APP_API_KEY,
  authDomain: process.env.REACT_APP_AUTH_DOMAIN,
  databaseURL: process.env.REACT_APP_DATABASE_URL,
  projectId: process.env.REACT_APP_PROJECT_ID,
  storageBucket: process.env.REACT_APP_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_ID,
  measurementId: process.env.REACT_APP_MEASUREMENT_ID,
}

class Firebase {
    constructor() {
      app.initializeApp(config);
      this.auth = app.auth();
      this.db = app.database();
    }

    doSignInWithEmailAndPassword = (email, password) =>
        this.auth.signInWithEmailAndPassword(email, password);

    doSignOut = () => this.auth.signOut();

    onAuthUserListener = (next, fallback) =>
    this.auth.onAuthStateChanged(authUser => {
      if (authUser) {
        console.log(authUser);
            next(authUser);
          
      } else {
        fallback();
      }
    });

    encendido = () => this.db.ref('Encendido');
    velocidad = () => this.db.ref('Velocidad');
    distancia = () => this.db.ref('Distancia');
    setEncendido = (val) => this.db.ref().update({Encendido: val})
  }
  export default Firebase;
