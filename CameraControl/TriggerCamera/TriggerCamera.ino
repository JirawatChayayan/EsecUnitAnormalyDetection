#include "triggerstate.h"
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

TriggerInput inputRun(12,20);
TriggerInput inputSetupTrain(11,30);
TriggerInput inputSetupTest(10,30);


const int sigPin1 =  2;
const int sigPin2 =  3;
const int sigPin3 =  4;

bool sigState1 = HIGH;
bool sigState2 = HIGH;
bool sigState3 = HIGH;

unsigned long previousMillis1 = 0;
unsigned long previousMillis2 = 0;
unsigned long previousMillis3 = 0;

const long interval1 = 100;
const long interval2 = 400;
const long interval3 = 200;



bool SetupMode = true;
void setup() {
  pinMode(sigPin1, OUTPUT);
  pinMode(sigPin2, OUTPUT);
  pinMode(sigPin3, OUTPUT);
  digitalWrite(sigPin1, sigState1);
  digitalWrite(sigPin2, sigState2);
  digitalWrite(sigPin3, sigState3);
  Serial.begin(115200);
  delay(10);
  Serial.println();
  Serial.println("#####################################################################");
  Serial.println("# {\"Mode\":\"SetupTrain\"} {\"Mode\":\"SetupTest\"} and {\"Mode\":\"Process\"} #");
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
    signalGen1();
    signalGen2();
    signalGen3();
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

void signalGen1()
{
   unsigned long currentMillis = millis();

  if (currentMillis - previousMillis1 >= interval1) 
  {
    previousMillis1 = currentMillis;
    if (sigState1 == LOW) 
    {
      sigState1 = HIGH;
    } 
    else 
    {
      sigState1 = LOW;
    }
    digitalWrite(sigPin1, sigState1);
  }
}


void signalGen2()
{
   unsigned long currentMillis = millis();

  if (currentMillis - previousMillis2 >= interval2) 
  {
    previousMillis2 = currentMillis;
    if (sigState2 == LOW) 
    {
      sigState2 = HIGH;
    } 
    else 
    {
      sigState2 = LOW;
    }
    digitalWrite(sigPin2, sigState2);
  }
}

void signalGen3()
{
   unsigned long currentMillis = millis();

  if (currentMillis - previousMillis3 >= interval3) 
  {
    previousMillis3 = currentMillis;
    if (sigState3 == LOW) 
    {
      sigState3 = HIGH;
    } 
    else 
    {
      sigState3 = LOW;
    }
    digitalWrite(sigPin3, sigState3);
  }
}
