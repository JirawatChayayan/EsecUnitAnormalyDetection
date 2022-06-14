#include <ArduinoJson.h>
#include "triggerstate.h"


const uint8_t Ix10[8] = {39,36,35,34,21,19,18,4};
const uint8_t Qx10[8] = {13,14,27,26,25,33,32,2};

TriggerInput inputRun(Ix10[0],20);
TriggerInput inputSetupTrain(Ix10[1],30);
TriggerInput inputSetupTest(Ix10[2],30);

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
bool SetupMode = true;

unsigned long previousMillisToggle = 0; 
unsigned long previousMillisHandcheck = 0; 

DynamicJsonDocument doc(1024);

void setup() {
  pinMode(5,OUTPUT);
  for(int i = 0; i<8; i++)
  {
      pinMode(Qx10[i],OUTPUT);
      digitalWrite(Qx10[i],false);
  }

  Serial.begin(115200);
  delay(10);
  Serial.println("#####################################################################");
}



void loop() 
{
    
    bool ipRun = inputRun.getState();
    bool ipTrain = inputSetupTrain.getState();
    bool ipTest = inputSetupTest.getState();
    if(ipRun)
    {
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
    }
    toggle();
    handcheck();
    IOControl();
}

void toggle()
{
   unsigned int interval = 500;  
   if (millis() - previousMillisToggle  >= interval) 
   {
      previousMillisToggle = millis();
      digitalWrite(5,!(digitalRead(5)));
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
   unsigned int interval = 1000;  
   if (millis() - previousMillisHandcheck  >= interval) 
   {
      previousMillisHandcheck = millis();
      if(digitalRead(Qx10[0]))
      {
        Serial.println("HandCheck;{\"StopMC\":true}");
      }
      else
      {
        Serial.println("HandCheck;{\"StopMC\":false}");
      }
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
   }
}
void serialIO(JsonObject obj)
{
  if (obj.containsKey("StopMC")) 
  {
    bool stopMC = obj["StopMC"].as<bool>();
    digitalWrite(Qx10[0],stopMC);
  }
  else if (obj.containsKey("SetOutput")) 
  {
    int ioPort = obj["SetOutput"].as<int>();
    if(!(ioPort<1 && ioPort>7))
    {
      digitalWrite(Qx10[ioPort],true);
    }
  }
  else if (obj.containsKey("ResetOutput")) 
  {
    int ioPort = obj["ResetOutput"].as<int>();
    if(!(ioPort<1 && ioPort>7))
    {
      digitalWrite(Qx10[ioPort],false);
    }
  }
  else if (obj.containsKey("AllOutput")) 
  {
    bool allon = obj["AllOutput"].as<bool>();
    for(int i = 1; i<8; i++)
    {
      digitalWrite(Qx10[i],allon);
    }
  }
}
