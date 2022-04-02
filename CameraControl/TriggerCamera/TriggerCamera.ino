#include "triggerstate.h"
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

TriggerInput inputRun(12,20);
TriggerInput inputSetupTrain(11,30);
TriggerInput inputSetupTest(10,30);

bool SetupMode = true;
void setup() {
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
