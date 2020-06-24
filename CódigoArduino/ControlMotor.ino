#include <Servo.h>

//Control velocidad
const int pinMotor = 6;
const int pinHall = 3;
const float radioRueda = 23;   

//Marcas de tiempo para saber lo que tarda la rueda en dar una vuelta
volatile float tiempo0;
volatile float tiempo1;
volatile float tiempo2;
volatile float tiempo3;
volatile float tiempo4;


float VEL = 0.00; //Velocidad actual del motor
float distancia = 0; //Distancia total recorrida
int velocidades[] = {9,10,11,12,13}; //Velocidades que tendrá el motor en km/h
int velActual = 0; //Velocidad dentro del array de velocidades actual

const int inicioPwmMotor = 50; //Valor inicial pwm del motor 
int pwmMotor = inicioPwmMotor; //Salida pwm al motor, es 50 ya que al arrancar el coche necesitaremos más corriente
bool cocheEncendido = true; //Booleano para saber si el coche está encencido o apagado

int contador = 0; //Contador para no enviar la distancia recorrida siempre

//Control giro
Servo servo;
const int pinServo = 4;
int anguloServo = 90;
int constanteGiro = 5;

//Inicializamos
void setup() {
  Serial.begin(9600);

  //Motor
  pinMode (pinMotor, OUTPUT);
  analogWrite(pinMotor, 0);
  pinMode(pinHall, INPUT);
  
  tiempo1 = micros();
  tiempo2 = micros();
  tiempo4 = micros();
  
  //Declaramos la interrupcion. 
  servo.attach(pinServo);
}

//Bucle que se ejecuta siempre
void loop() {
  //Recibimos señal por el puerto USB
  while (Serial.available() > 0) {
    char s = Serial.read();   
    if (s == '0') izquierda();
    else if (s == '1') derecha();
    else if (s == '2') parar();
    else if (s == '3') arrancar();
  }

  if (cocheEncendido){
    //Cada 400 metros cambiamos de velocidad
    if (distancia > 40000){
      //Si no hemos llegado al final de la lista de velocidades y hemos recorrido 400 metros pasamos a la siguiente velocidad
      //y se la enviamos a la Raspberri Pi
      if (velActual < 4) {
        velActual++;
        String s = "Velocidad " + String(velocidades[velActual]);
        Serial.println(s); //Enviamos la velocidad
      }
        distancia = 0;
    }
    tiempo3 = micros();
    //Cuando estamos parados aceleramos rápido
    if (VEL == 0) {
      if ((tiempo3 - tiempo4) > 1000){
        i++;
        analogWrite(IN1, i);
      }
      tiempo4 = micros();
    }
    //Cuando estamos en movimiento ajustamos la velocidad cada cierto tiempo
    if ((tiempo3 - tiempo2) > 100000){
      if (VEL  < velocidades[velActual]){
        i++;
        analogWrite(IN1, i);
      }
      if (VEL > velocidades[velActual]){
        i--;
        analogWrite(IN1, i);
      }
     tiempo2 = micros();
    }
    //Enviamos la distancia a la Raspberri Pi cada cierto tiempo
    if (contador == 30000){
      String s = "Distancia " + String(distancia + velActual*40000);
      Serial.println(s); //Enviamos la distancia
      contador = 0;
    }else {
      contador++;
    }
  }

  
}

//Recibimos señal del sensor Hall, y pasamos de cm/microseg a km/h
void pulsoRueda(){
  if (cocheEncendido){
    tiempo1 = micros();
    VEL = radioRueda*36000/ ((tiempo1 - tiempo0));
    distancia = distancia + radioRueda;
    tiempo0 = tiempo1;
  }
}

void arrancar(){
  cocheEncendido = true;
}

void parar(){
  cocheEncendido = false;
}

void derecha(){
  anguloServo = anguloServo - constanteGiro;
  servo.write(anguloServo);
}

void izquierda(){
  anguloServo = anguloServo + constanteGiro;
  servo.write(anguloServo);
}
