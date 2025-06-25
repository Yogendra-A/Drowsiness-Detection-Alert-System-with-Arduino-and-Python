#include <Wire.h>
#include <LiquidCrystal_I2C.h>

//LCD 
LiquidCrystal_I2C lcd(0x27, 16, 2);

int buzzerPin = 8;  

void setup() {
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
  lcd.init();                       
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("System Ready");      
  
}

void loop() {
  if (Serial.available() > 0) {
    lcd.clear();                   
    char signal = Serial.read();   
    Serial.print("Received Signal: "); 
    Serial.println(signal);

    if (signal == '2') {           
      lcd.print("Eyes Closed");
      digitalWrite(buzzerPin, HIGH);
      delay(200);                 
      digitalWrite(buzzerPin, LOW);
    } else if (signal == '0') {    
      lcd.print("Eyes Open");
    } else {
      lcd.print("System Ready");   
    }
  }
}