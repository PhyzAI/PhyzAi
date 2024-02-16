/* Include the HCPCA9685 library */
#include "HCPCA9685.h"

/* I2C slave address for the device/module. For the HCMODU0097 the default I2C address
   is 0x40 */
#define I2CAdd 0x40
HCPCA9685 HCPCA9685(I2CAdd);

void setup() 
{
  HCPCA9685.Init(SERVO_MODE); /* Wake the device up */
  HCPCA9685.Sleep(false);
  Serial.begin(9600); // Start Communication
  HCPCA9685.Servo(15, 0); // move servo to 0 degrees
  delay(25); // wait some time (its in all examples
}


void loop() 
{
  int Pos;
 
  /* Sweep the servo back and forth from its minimum to maximum position. If your servo is hitting its end stops then you should adjust the values so that the servo can sweep though its full range without hitting the end stops. You can adjust the min & max positions by altering the trim values in the libraries HCPCA9685.h file*/
 
  for(Pos = 10; Pos< 450; Pos++)
 
  {
 
    /* This function sets the servos position. It takes two parameters,
 
     * the first is the servo to control, and the second is the servo
 
     * position. */
 
HCPCA9685.Servo(15, Pos);
 
delay(10);
 
  }
 
for(Pos = 450; Pos>= 10; Pos--)
 
  {
 
HCPCA9685.Servo(15, Pos);
 
delay(10);
 
  }
}
