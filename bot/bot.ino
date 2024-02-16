#include "HCPCA9685.h"

/* I2C slave address for the device/module. For the HCMODU0097 the default I2C address
   is 0x40 */
#define I2CAdd 0x40
HCPCA9685 HCPCA9685(I2CAdd);

int currentHead = 1;
int currentLArm = 1;
int currentRArm = 1;
char currentCase = 'l';
int Pos = 240;

void setup()
{
  //An LED is Connected Pin12 
  Serial.begin(9600); 

  HCPCA9685.Init(SERVO_MODE); 
  HCPCA9685.Sleep(false);
  HCPCA9685.Servo(15, Pos); //head
  HCPCA9685.Servo(14, Pos); //left arm
  delay(10); 
}

void loop()
{

 if (Serial.available()) 
    {
      currentCase = Serial.read();    
       
      switch(currentCase) {
        case '1':  
          //head left
          if (currentHead == 1) {
            for(Pos; Pos <= 300; Pos++) {
              HCPCA9685.Servo(15, Pos);
              delay(1);
            }
            currentHead = 0;
            break;
          }
          //head right
          else if (currentHead == 0) {
            for(Pos; Pos >= 180; Pos--) {
              HCPCA9685.Servo(15, Pos);
              delay(1);
            }
            currentHead = 1;
            break;
          }

        case '2':
          if (currentLArm == 1) {
            for(Pos; Pos <= 300; Pos++) {
              HCPCA9685.Servo(14, Pos);
              delay(1);
            }
            currentLArm = 0;
            break;
          }
          //head right
          else if (currentLArm == 0) {
            for(Pos; Pos >= 180; Pos--) {
              HCPCA9685.Servo(14, Pos);
              delay(1);
            }
            currentLArm = 1;
            break;
          }
        
        case '3':
          if (currentRArm == 1) {
            for(Pos; Pos <= 300; Pos++) {
              HCPCA9685.Servo(13, Pos);
              delay(1);
            }
            currentRArm = 0;
            break;
          }
          //head right
          else if (currentRArm == 0) {
            for(Pos; Pos >= 180; Pos--) {
              HCPCA9685.Servo(13, Pos);
              delay(1);
            }
            currentRArm = 1;
            break;
          }

        default:
          break;
      }
    }
}