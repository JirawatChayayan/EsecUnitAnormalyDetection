#include <ArduinoJson.h>
#include "triggerstate.h"

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);



#define testSigPin 10
#define togglePin 40
#define StopMcPin 6
#define StopMcPinTrig 7
#define trigRun 27
#define trigTrain 37
#define trigTest 47
#define trigRelease 53


TriggerInput inputRun(trigRun,20);
TriggerInput inputSetupTrain(trigTrain,30);
TriggerInput inputSetupTest(trigTest,30);
TriggerInput inputRelease(trigRelease,30);

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
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
bool disp_init = false;

bool stopTrigged = false;



DynamicJsonDocument doc(1024);

void setup() {
  Serial.begin(9600);
  pinMode(testSigPin, OUTPUT);
  pinMode(togglePin, OUTPUT);
  pinMode(StopMcPin, OUTPUT);
  pinMode(StopMcPinTrig, OUTPUT);
  digitalWrite(StopMcPin, HIGH);
  digitalWrite(StopMcPinTrig, HIGH);
  initialDisp();
  delay(10);
  Serial.println("#####################################################################");
}



void loop() 
{
    bool ipRun = inputRun.getState();
    bool ipTrain = inputSetupTrain.getState();
    bool ipTest = inputSetupTest.getState();
    bool ipRelease = inputRelease.getState();
    if(ipRun)
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
    IOControl();
    rateCal();
    toggleStop();
    //toggleSignal();
    togleDispStopMC();
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
    unsigned int interval = 500;
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
    Serial.println("HandCheck;{\"StopMC\":true}");
  }
  else
  {
    Serial.println("HandCheck;{\"StopMC\":false}");
  }
}

void rateCal()
{
  unsigned int interval = 2000;
  if (millis() - previousMillisRateCount  >= interval)
  {
    previousMillisRateCount = millis();
    String res = dataCount; 
    dataCount = "";
    //Serial.println(res);
    Rate = calculate(res);
    //Serial.println(Rate);
    if(digitalRead(StopMcPin))
    {
      dispRate();
    }
    
  }
}

void counter()
{
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
        if(dataPeriode < 1000)
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



void IOControl()
{
    while (Serial.available()) 
    {
      char inChar = (char)Serial.read();
      if (inChar == '\n') 
      {
        stringComplete = true;
      }
      else
      {
        inputString += inChar;
      }
   }
   if (stringComplete) 
   {
      String dataInput = inputString;
      inputString = "";
      stringComplete = false;
      
      JsonObject obj = doc.as<JsonObject>();
      deserializeJson(doc, dataInput);
      
      serialIO(obj);
      serialDisp(obj);
   }
}
void serialIO(JsonObject obj)
{
  if (obj.containsKey("StopMC"))
  {
    bool stopMC = obj["StopMC"].as<bool>();
    digitalWrite(StopMcPin, !stopMC);
    handcheck_msg();
    handcheck_msg();
    handcheck_msg();
  }
}

void serialDisp(JsonObject obj)
{

  bool hasChange = false;
  if (obj.containsKey("MC_ID") || obj.containsKey("MAC") || obj.containsKey("IP"))
  {
    if (obj.containsKey("IP"))
    {
      String ip = obj["IP"].as<String>();
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
    if (obj.containsKey("MAC"))
    {
      String mac = obj["MAC"].as<String>();
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
    if (obj.containsKey("MC_ID"))
    {
      String mcid = obj["MC_ID"].as<String>();
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

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;){
      Serial.println(F("SSD1306 allocation failed"));
      delay(1000);
    }
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
  display.display();
  delay(20);
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

  dispMAC();

  dispMCID();

  dispRate();

  

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
//  else
//  {
//    display.setTextColor(BLACK);
//  }
  

}
