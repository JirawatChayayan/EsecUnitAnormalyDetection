#include "triggerstate.h"

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
//#include <avr/wdt.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);



#define testSigPin 10
#define togglePin 40
#define StopMcPin 7
#define StopMcPinTrig 6
#define trigRun 27
#define trigTrain 37
#define trigTest 47
#define trigRelease 53


TriggerInput inputRun(trigRun,20);
TriggerInput inputSetupTrain(trigTrain,30);
TriggerInput inputSetupTest(trigTest,30);
TriggerInput inputRelease(trigRelease,30);


bool SetupMode = true;

unsigned long startCount = 0; 
String dataCount = "";


unsigned long previousMillisToggleDisp = 0;
unsigned long previousMillisToggleStop = 0;
unsigned long previousMillisToggleSig = 0;
unsigned long previousMillisToggle = 0; 
unsigned long previousMillisHandcheck = 0; 
unsigned long previousMillisRateCount = 0; 

String IP = "192.168.137.223";
String MAC =  "70-9C-D1-22-82-6F";
String MC_ID = "ESEC2008-96P";
int Rate = 0;
int triggerCount = 0;
int procCounterTrig = 0;
bool disp_init = false;

bool stopTrigged = false;




void setup() {
  Serial.begin(115200);
  pinMode(testSigPin, OUTPUT);
  pinMode(togglePin, OUTPUT);
  pinMode(StopMcPin, OUTPUT);
  pinMode(StopMcPinTrig, OUTPUT);
  digitalWrite(StopMcPin, HIGH);
  digitalWrite(StopMcPinTrig, HIGH);
  //initialDisp();

//  Serial.println("***********************************************************************************");
//  Serial.println("*  Mode.                   :IP, :MAC, :MC_ID, :STOP, :RELEASE ,:{ip}:{mac}:{mcid} *");
//  Serial.println("*  Example IP Config.      :IP:192.168.137.1;                                     *");
//  Serial.println("*  Example MAC Config.     :MAC:70-9C-D1-22-82-6F;                                *");
//  Serial.println("*  Example MC_ID Config.   :MC_ID:ESEC2008-96P;                                   *");
//  Serial.println("*  Example All Config.     :192.168.137.1:70-9C-D1-22-82-6F:ESEC2008-96P;         *");
//  Serial.println("***********************************************************************************\n\n");
  //wdt_enable(WDTO_500MS);
}



void loop() 
{
    bool ipRun = inputRun.getState();
    bool ipTrain = inputSetupTrain.getState();
    bool ipTest = inputSetupTest.getState();
    bool ipRelease = inputRelease.getState();
    if(ipRun && digitalRead(StopMcPin))
    {
        counter();
        String res = "{\"Mode\":\"Process\"}";
        printMsg(false,res);
    }
    else
    {
        if(ipTrain)
        {
            String res = "{\"Mode\":\"SetupTrain\"}";
            printMsg(false,res);
        }
        else if(ipTest)
        {
            String res = "{\"Mode\":\"SetupTest\"}";
            printMsg(false,res);
        }
        else if(ipRelease)
        {
          digitalWrite(StopMcPin, !digitalRead(StopMcPin));
          handcheck_msg();
        }
    }
    toggle();
    handcheck();
    //IOControl();
    rateCal();
    toggleStop();
    //toggleSignal();
    togleDispStopMC();
    //wdt_reset();
}


bool disptog = false;
bool resetToNormDisp = false;
void togleDispStopMC()
{
  if(!digitalRead(StopMcPin))
  {
    resetToNormDisp = true;
    unsigned int interval = 300;
    if(millis() - previousMillisToggleDisp >= interval)
    {
      previousMillisToggleDisp = millis();
      dispStopMC(disptog);
      disptog = !disptog;
    }
  }
  else
  {
    if(resetToNormDisp)
    {
      resetToNormDisp = false;
      normalDisp();
    }
  }
}



int countTrig = 0;
void toggleStop()
{
  if(!digitalRead(StopMcPin))
  {
    if(stopTrigged)
    {
      return;
    }
    unsigned int interval = 1500;
    if(millis() - previousMillisToggleStop >= interval)
    {
      previousMillisToggleStop = millis();
      digitalWrite(StopMcPinTrig, !digitalRead(StopMcPinTrig));
      countTrig += 1;
      if(countTrig == 2)
      {
        stopTrigged = true;
      }
    }
  }
  else
  {
    digitalWrite(StopMcPinTrig, HIGH);
    stopTrigged = false;
    countTrig = 0;
  }
}

void toggleSignal()
{
   unsigned int interval = 200;  
   if (millis() - previousMillisToggleSig  >= interval) 
   {
      previousMillisToggleSig = millis();
      digitalWrite(testSigPin, !digitalRead(testSigPin));
   }
}

void toggle()
{
   unsigned int interval = 500;  
   if (millis() - previousMillisToggle  >= interval) 
   {
      previousMillisToggle = millis();
      digitalWrite(togglePin,!(digitalRead(togglePin)));
   }
} 

void printMsg(bool command,String val)
{
    if(command)
    {
        String s1 = "CommandInput >> ";
        String s3 = s1 + val;
        Serial.println(s3); 
    }
    else
    {
        String s1 = "Trig;";
        String s3 = s1 + val;
        Serial.println(s3);
    }
}
void handcheck()
{

  unsigned int interval = 2000;
  if (millis() - previousMillisHandcheck  >= interval)
  {
    previousMillisHandcheck = millis();
    handcheck_msg();
  }
}

void handcheck_msg()
{
  if (!digitalRead(StopMcPin))
  {
    Serial.println("HandCheck;{\"StopMC\":true,\"Rate\":"+String(Rate)+",\"TriggerCount\":"+String(procCounterTrig)+"}");
  }
  else
  {
    Serial.println("HandCheck;{\"StopMC\":false,\"Rate\":"+String(Rate)+",\"TriggerCount\":"+String(procCounterTrig)+"}");
  }
}

void rateCal()
{
  unsigned int interval = 5000;
  if (millis() - previousMillisRateCount  >= interval)
  {
    previousMillisRateCount = millis();
    if(digitalRead(StopMcPin))
    {
      String res = dataCount; 
      dataCount = "";
      procCounterTrig = triggerCount;
      triggerCount =0;
      startCount = 0;
      Serial.println(res);
      Rate = calculate(res);
      dispRate();
    }
    else
    {
      dataCount = "";
      Rate = 0;
      triggerCount =0;
      procCounterTrig = 0;
    }
    
  }
}

void counter()
{
  triggerCount +=1;
  if(startCount == 0)
  {
    startCount = millis();
  }
  else
  {
    unsigned long cal = millis()-startCount;
    startCount = 0;
    if(dataCount == "")
    {
      dataCount += String(cal);
    }
    else
    {
      dataCount += "," + String(cal);
    }
  }
}

int calculate(String res)
{
    if(res == "")
    {
      return 0;
    }
    String s = res+",";
    int n = s.length();
    char char_array[n + 1];
    strcpy(char_array, s.c_str());
    String buff = "";
    int idx = 0;
    int sumdata = 0;
    for(int i =0; i<n; i++)
    {
      if(char_array[i] == ',')
      {
        unsigned long dataPeriode = atol(buff.c_str());
        if(dataPeriode < 3000)
        {
          sumdata += dataPeriode;
          idx +=1;
        }
        buff = "";
       
      }
      else
      {
        buff += char_array[i];
      }
    }
    if(sumdata != 0 && idx != 0)
    {
       int T_avg = (sumdata)/(idx);
       return T_avg;
    }
    else
    {
      return 0;
    }
}


String Allkey = ""; 
int i=0;
String Key = "";
String Val = "";
String Val2 = "";
bool stringComplete = false;  // whether the string is complete

void serialEvent() 
{ 
 /// wdt_reset();
  while(Serial.available()>0)
  {
      char A = (char)Serial.read();
      if(A=='\n')
      {        
//        Serial.println("COMMAND := "+Allkey);
//        Serial.println("Key := "+Key);
//        Serial.println("Val := "+Val);
//        Serial.println("Val := "+Val2);
//        Serial.println("I := " + String(i));
        if(i == 1)
        {
        //  wdt_reset();
          serialIO(Key);
      //    wdt_reset();
        }
        else if(i == 2)
        {
       //   wdt_reset();
          serialDisp(Key,Val);
       //   wdt_reset();
        }
        else if(i == 3)
        {
      //    wdt_reset();
          serialDisp2(Key,Val,Val2);
        //  wdt_reset();
        }
        i = 0;
        Key = "";
        Val = "";
        Val2 = "";
        Allkey = "";
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
          }
  
        }
      }
  }
  Serial.flush();
}

void serialIO(String cmd)
{
  //:STOP, :RELEASE 
  if (cmd == "STOP" || cmd == "Stop" || cmd == "stop")
  {
    if(!digitalRead(StopMcPin))
    {
      return;
    }
    digitalWrite(StopMcPin, LOW);
    Rate = 0;
    handcheck_msg();
    handcheck_msg();
  }
  if (cmd == "RELEASE" || cmd == "Release" || cmd == "release")
  {
    if(digitalRead(StopMcPin))
    {
      return;
    }
    digitalWrite(StopMcPin, HIGH);
    Rate = 0;
    handcheck_msg();
    handcheck_msg();
  }
}



void serialDisp2(String ip,String mac,String mcid)
{
  bool hasChange = false;
  if (ip != IP)
  {
    if(ip == "null" || ip == "")
    {
      return;
    }
    IP = ip;
    hasChange = true;
  }
  if (mac != MAC)
  {
    if(mac == "null" || mac == "")
    {
      return;
    }
    MAC = mac;
    hasChange = true;
  }
  if (mcid != MC_ID)
  {
    if(mcid == "null" || mcid == "")
    {
      return;
    }
    MC_ID = mcid;
    hasChange = true;
  }
  if(hasChange)
  {
    normalDisp();
  }
}



void serialDisp(String cmd,String val)
{
  Serial.println("Key := "+cmd);
  Serial.println("Val := "+val);
  if(val == "" || val == "null")
  {
    return;
  }
  //:IP, :MAC, :MC_ID
  bool hasChange = false;
  if (cmd == "MC_ID" || cmd == "MAC" || cmd == "IP")
  {
    if (cmd == "IP")
    {
      String ip = val;
      if (ip != IP)
      {
        if(ip == "null")
        {
          return;
        }
        IP = ip;
        hasChange = true;
      }
    }
    if (cmd == "MAC")
    {
      String mac = val;
      if (mac != MAC)
      {
        if(mac == "null")
        {
          return;
        }
        MAC = mac;
        hasChange = true;
      }
    }
    if (cmd == "MC_ID")
    {
      String mcid = val;
      if (mcid != MC_ID)
      {
        if(mcid == "null")
        {
          return;
        }
        MC_ID = mcid;
        hasChange = true;
      }
    }
    if(hasChange)
    {
      normalDisp();
    }
  }
}

void initialDisp()
{
  return;
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) 
  {
//  Serial.println(F("SSD1306 allocation failed"));
//  for (;;)
//  {
//    Serial.println(F("SSD1306 allocation failed"));
//    delay(1000);
//  }
    return;
  }
  disp_init = true;
  normalDisp();
}
void normalDisp()
{
  if(!disp_init)
  {
    return;
  }
  if(!digitalRead(StopMcPin))
  {
    return;
  }
  display.display();
  delay(1);
  display.clearDisplay();
  display.setTextSize(1); // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.fillRect(0, 0, display.width(), 12, SSD1306_INVERSE);
  display.display(); // Update screen with each newly-drawn rectangle

  display.setTextColor(SSD1306_BLACK);
  display.setCursor(4, 2);
  display.print("ESEC Anormaly Detect");
  display.display();

  dispIP();
 // wdt_reset();
  dispMAC();
//  wdt_reset();
  dispMCID();
 // wdt_reset();
  dispRate();
 // wdt_reset();
  

}

void dispMCID()
{
  if(!disp_init)
  {
    return;
  }
  display.setTextColor(WHITE, BLACK);
  display.setCursor(0, 38);
  display.println("                          ");
  display.display();
  display.setCursor(0, 38);
  display.print("M/C ID ");
  display.print(MC_ID);
  display.display();
}

void dispMAC()
{
    if(!disp_init)
  {
    return;
  }
  display.setTextColor(WHITE, BLACK);
  display.setCursor(0, 27);
  display.println("                        ");
  display.display();
  display.setCursor(0, 27);
  display.print("MAC ");
  display.print(MAC);
  display.display();
}

void dispIP()
{
    if(!disp_init)
  {
    return;
  }
  display.setTextColor(WHITE, BLACK);
  display.setCursor(0, 16);
  display.println("                      ");
  display.display();
  display.setCursor(0, 16);
  display.print("IP ");
  display.print(IP);
  display.print("    ");
  display.display();
}

void dispRate()
{
    if(!disp_init)
  {
    return;
  }
  display.setTextColor(WHITE,BLACK);
  display.setCursor(0, 49);
  display.print("Rate ");
  display.print(String(Rate));
  display.print(" mS   ");
  display.display();
}

void dispStopMC(bool white)
{
  if(!disp_init)
  {
    return;
  }
  display.clearDisplay();
  if(white)
  {
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(40, 4);
    display.print("Stop");
    display.setCursor(25, 25);
    display.print("Machine");
    display.setCursor(13, 46);
    display.print("By AI !!!");
    display.setTextSize(1);
    
  }
  display.display();

}
