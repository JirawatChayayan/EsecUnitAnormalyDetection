#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

// Set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27, 16, 4);

/*startCursor 
 * Line 1 = 0,0
 * Line 2 = 0,1
 * line 3 = 16,0
 * line 4 = 16,1
*/

bool serialConnected = false;
bool alarmStatus = false;

String IP = "172.16.40.252";
int Rate = 1500;
int Trigger = 10;

bool runDispIp = false;
bool runDispAlarm = false;
bool stateLed = false;
unsigned long lastBlinkTime = 0;
unsigned long lastBlinkTimeLED = 0;
bool ip_displayed = false;
bool rate_displayed = false;
bool trigger_displayed = false;
String last_IP = "";
int last_Rate = 0;
int last_trigger = 0;
unsigned long prevTimeMessage = 0;


String Allkey = ""; 
int i=0;
String Key = "";
String Val = "";
String Val2 = "";
String Val3 = "";

#define red 7
#define green 8
#define blue 9

void setup()
{
  init_lcd();
  Serial.begin(115200);
  prevTimeMessage = millis();
  pinMode(red,OUTPUT);
  pinMode(green,OUTPUT);
  pinMode(blue,OUTPUT);
}

void loop()
{

  checkConnectSerial();

  digitalWrite(blue,false);
  
  if(alarmStatus)
  {
     ip_displayed = false;
     rate_displayed = false;
     trigger_displayed = false;
     if(runDispAlarm = false)
     {
       runDispIp = false;
       runDispAlarm = true;
       clearDisp();
       delay(10);
       clearDisp();
       lcd.backlight();
     }
     displayAlarm();
  }
  else
  {
     if(runDispIp = false)
     {
       runDispIp = true;
       runDispAlarm = false;
       clearDisp();
       delay(10);
       clearDisp();
       lcd.backlight();
     }
      dispIP();
      dispRate();
      dispTrigger();
      
  }
  blinkDisplay();
  blinkStatus();
}

void blinkStatus()
{
  if(!serialConnected)
  {
    digitalWrite(red,false);
    digitalWrite(green,false);
    return;
  }
  int pin = red;
  if(alarmStatus)
  {
    digitalWrite(green,false);
    digitalWrite(blue,false);
    pin = red;
  }
  else
  {
    digitalWrite(red,false);
    digitalWrite(blue,false);
    pin = green;
  }
  if(millis() - lastBlinkTimeLED >= 150)
  {
     lastBlinkTimeLED = millis();
     toggle_led(pin);
  }
}

void serialEvent() 
{
  while (Serial.available()) 
  {
    prevTimeMessage = millis();
    serialConnected = true;
    char A = (char)Serial.read();
    
    if (A == '\n') 
    {
      //stringComplete = true;
      if(Key == "IP")
      {
        IP = Val;
      }
      else if(Key == "Rate")
      {
        Rate = Val.toInt();
      }
      else if(Key == "Trig")
      {
        Trigger = Val.toInt();
      }
      else if(Key == "Alarm")
      {
        clearDisp();
        ip_displayed = false;
        rate_displayed = false;
        trigger_displayed = false;
        alarmStatus = Val == "true";
      }
      else
      {
        if(i==3)
        {
           alarmStatus = Key == "true";
           if(alarmStatus)
           {
                ip_displayed = false;
                rate_displayed = false;
           }
           Rate = Val.toInt();
           Trigger = Val2.toInt();
        }
        else if(i==4)
        {
           alarmStatus = Key == "true";
           if(alarmStatus)
           {
                ip_displayed = false;
                rate_displayed = false;
           }
           Rate = Val.toInt();
           Trigger = Val2.toInt();
           IP = Val3;
        }
      }
      Serial.println(Allkey);
      Key = "";
      Val = "";
      Val2 = "";
      Val3 = "";
      Allkey = "";
      i=0;
    }
    else
    {
      Allkey += A;
      if(String(A) == ":" || A == ':' )
      {
         i+=1;
      }
      else if(A !='\n' && A != '\r'!= (String(A) == ";" || A == ';'))
      {
          switch(i)
          {
            case 1:
              Key += A;
              break;
            case 2:
              Val += A;
              break;
            case 3:
              Val2 += A;
              break;
            case 4:
              Val3 += A;
              break;
          }
      }
    }
  }
}

/********************* Function *********************/


void init_lcd()
{ 
  byte customChar[] = {
                      B11111,
                      B11111,
                      B11111,
                      B11111,
                      B11111,
                      B11111,
                      B11111,
                      B11111
                    };
  byte customChar2[] = {
                          B11111,
                          B10001,
                          B10001,
                          B10001,
                          B10001,
                          B10001,
                          B10001,
                          B11111
                        };
  lcd.begin();
  lcd.createChar(0, customChar);
  lcd.createChar(1, customChar2);
}


void blinkDisplay()
{
  if(alarmStatus)
  {
    if(millis()-lastBlinkTime >150)
    {
        lastBlinkTime = millis();
        if(stateLed)
        {
          lcd.backlight();
          stateLed = false;
        }
        else
        {
          lcd.noBacklight();
          stateLed = true;
        }
    }
  }
  else
  {
     lcd.backlight();
     stateLed = false;
  }
 
}

void dispIP()
{

  lcd.backlight();
  if(!ip_displayed || (IP != last_IP))
  {
      lcd.setCursor(0,0);
      lcd.print("                ");
      lcd.setCursor(0,1);
      lcd.print("                ");
    
      
      lcd.setCursor(0,0);
      lcd.print("IP:");
      lcd.setCursor(0,1);
      lcd.print(IP);
      last_IP = IP;
      ip_displayed = true;
  }
}

void dispRate()
{
  lcd.backlight();
  if(!rate_displayed || (Rate != last_Rate))
  {
    lcd.setCursor(16,1);
    lcd.print("                ");
    
    lcd.setCursor(16,1);
    lcd.print("Rate: "+String(Rate)+" ms");
    last_Rate = Rate;
    rate_displayed = true;
  }
}

void dispTrigger()
{
  lcd.backlight();
  if(!trigger_displayed || (Trigger != last_trigger))
  {
    lcd.setCursor(16,0);
    lcd.print("                ");
    lcd.setCursor(16,0);
    lcd.print("                ");
    Serial.println("Trigger");
    lcd.setCursor(16,0);
    lcd.print("Trig: "+String(Trigger));
    last_trigger = Trigger;
    trigger_displayed = true;
  }
}

void displayAlarm()
{
  lcd.setCursor(0,1);
  lcd.print("  Stop Machine  ");
  lcd.setCursor(16,0);
  lcd.print(" From AI System ");
  lcd.setCursor(0,0);
  lcd.print("----------------");
  lcd.setCursor(16,1);
  lcd.print("----------------");
}

void toggle_led(int pin)
{
  digitalWrite(pin,!digitalRead(pin));
}
void checkConnectSerial()
{
  if(millis()- prevTimeMessage>15000)
  {
    serialConnected = false;
  }
  if(serialConnected)
  {
    return;
  }


  ip_displayed = false;
  rate_displayed = false;
  trigger_displayed = false;
  clearDisp();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("UTAC  Automation");
  lcd.setCursor(0,1);
  lcd.print("Anormaly  System");
  lcd.setCursor(16,1);
  lcd.print("Booting ");
  int maxCount = 8;
  int count = -1;
  unsigned long prevTime = millis();
  int delayTime = 200;
  while(!serialConnected)
  {
    serialEvent();
    if(count == maxCount || count == -1)
    {
      lcd.setCursor(24,1);
      //lcd.print("         ");
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      lcd.write(1);
      if(millis()-prevTime >=delayTime)
      {
        toggle_led(blue);
        prevTime = millis();
        count =0;
      }
    }
    else
    {
      lcd.setCursor(24+count,1);
      lcd.write(0);
      if(millis()-prevTime >=delayTime)
      {
        prevTime = millis();
        count +=1;
        toggle_led(blue);
      }
    }
    
    if(serialConnected)
    {
      clearDisp();
      return;
    }
   
  }
}

void clearDisp()
{
  lcd.setCursor(0,0);
  lcd.print("                ");
  lcd.setCursor(0,1);
  lcd.print("                ");
  lcd.setCursor(16,0);
  lcd.print("                ");
  lcd.setCursor(16,1);
  lcd.print("                ");
}
