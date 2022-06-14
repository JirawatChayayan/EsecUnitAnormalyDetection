#include <ArduinoJson.h>
#include "triggerstate.h"

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <mutex>

SemaphoreHandle_t mutex = xSemaphoreCreateMutex();




#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);


const uint8_t Ix10[8] = {39,36,35,34,21,19,18,4};
const uint8_t Qx10[8] = {13,14,27,26,25,33,32,2};


TriggerInput inputRun(Ix10[0],20);
TriggerInput inputSetupTrain(Ix10[1],30);
TriggerInput inputSetupTest(Ix10[2],30);

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
bool SetupMode = true;

unsigned long previousMillis = 0; 
const long interval = 500;  


unsigned long previousMillisCountRate = 0; 
const long intervalRate = 60000;  


unsigned long startCount = 0; 
String dataCount = "";



String IP = "192.168.137.223";
String MAC =  "70-9C-D1-22-82-6F";
String MC_ID = "ESEC2008-96P";
String Rate = "0.00";

void setup() {
  assert(mutex);
  pinMode(5,OUTPUT);
  for(int i = 0; i<8; i++)
  {
      pinMode(Qx10[i],OUTPUT);
      digitalWrite(Qx10[i],false);
  }

  Serial.begin(115200);
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) 
  {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
    
  initialDisp();
  delay(10);
  Serial.println(" ");
  Serial.println("#####################################################################");
  Serial.println("# {\"Mode\":\"SetupTrain\"} {\"Mode\":\"SetupTest\"} and {\"Mode\":\"Process\"} #");
  Serial.println("#####################################################################");

  xTaskCreate(&disp_Task, "Disp_Task", 4096, NULL, 1, NULL);

  xTaskCreate(&main_Task, "Main_Task", 4096, NULL, 1, NULL);
  
}


void mainRun()
{
  while(1)
  {
    unsigned long currentMillis = millis();
    bool ipRun = inputRun.getState();
    bool ipTrain = inputSetupTrain.getState();
    bool ipTest = inputSetupTest.getState();
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
    }
    toggle(currentMillis);
  }
}

void dispRun()
{
  //pinMode(LED2, OUTPUT);
  
  //unsigned long previousMillisCountRate = 0;//millis(); 
  unsigned long currentMillis = 0;
  const long intervalRate = 10000;  
  String inputString = "";
  bool stringComplete = false;
  unsigned long mcCycle = 0;
  while(1) 
  {
      xSemaphoreTake(mutex, 10);
      bool avalible = Serial.available();
      xSemaphoreGive(mutex);
      while (avalible)
      {
        avalible = Serial.available();
        xSemaphoreTake(mutex, 10);
        char inChar = (char)Serial.read();
        xSemaphoreGive(mutex);
        if (inChar == '\n') 
        {
          stringComplete = true;
        }
        else
        {
          inputString += inChar;
        }
        mcCycle +=5;
      }
      xSemaphoreTake(mutex, 10);
      Serial.flush();
      xSemaphoreGive(mutex);
      if(stringComplete)
      {
        String dataInput = inputString;
        inputString = "";
        stringComplete = false;
        
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, dataInput);
        JsonObject obj = doc.as<JsonObject>();
        unsigned long res = serialIO(obj);
        if(res != 0)
        {
          mcCycle +=res;
        }
        else
        {
          if (obj.containsKey("IP")) 
          {
            String ip = obj["IP"].as<String>();
            if(ip != IP)
            {
              IP = ip;
            }
          }
          if (obj.containsKey("MAC")) 
          {
            String mac = obj["MAC"].as<String>();
            if(mac != MAC)
            {
              MAC = mac;
              
            }
          }
          if (obj.containsKey("MC_ID")) 
          {
            String mcid = obj["MC_ID"].as<String>();
            if(mcid != MC_ID)
            {
               MC_ID = mcid; 
            }
          }
          if(obj.containsKey("MC_ID") || obj.containsKey("MAC") || obj.containsKey("IP"))
          {
            dispIP();
            dispMAC();
            dispMCID();
            dispRate();
            mcCycle +=1000;
          }
        }
      }
      
      mcCycle +=1;
      if(mcCycle > 5000)
      {
        mcCycle = 0;
        previousMillisCountRate = currentMillis; 
        xSemaphoreTake(mutex, 50);
        String res = dataCount; 
        Serial.println(res);
        Rate = calculate(res);
        dispRate();
        dataCount = "";
        Serial.println(Rate);
        xSemaphoreGive(mutex); 
      }
      delay(2);
  }
}



void main_Task(void *p)
{
  mainRun();
}



void disp_Task(void *p)
{
  dispRun();
}

unsigned long serialIO(JsonObject obj)
{
  unsigned long mcCycle = 0;
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
    mcCycle +=200;
  }
  else if (obj.containsKey("ResetOutput")) 
  {
    int ioPort = obj["ResetOutput"].as<int>();
    if(!(ioPort<1 && ioPort>7))
    {
      digitalWrite(Qx10[ioPort],false);
    }
    mcCycle +=200;
  }
  else if (obj.containsKey("AllOutput")) 
  {
    bool allon = obj["AllOutput"].as<bool>();
    for(int i = 1; i<8; i++)
    {
      digitalWrite(Qx10[i],allon);
    }
    mcCycle +=200;
  }
  return mcCycle;
}

void loop() 
{
  //dispRun();
}


void counter()
{
  if(startCount == 0)
  {
    xSemaphoreTake(mutex, 50);
    startCount = millis();
    xSemaphoreGive(mutex);
  }
  else
  {
    xSemaphoreTake(mutex, 50);
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
    xSemaphoreGive(mutex);
  }
}

float calculate(String res)
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
        if(dataPeriode < 2000)
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
       float T_avg = (sumdata*1.00)/(idx*1.00);
       return T_avg;
    }
    else
    {
      return 0;
    }
}

void toggle(unsigned long currentMillis)
{
   if (currentMillis - previousMillis >= interval) 
   {
      previousMillis = currentMillis;
      digitalWrite(5,!(digitalRead(5)));
      handcheck();
      
   }
} 

void printMsg(bool command,String val)
{
    if(command)
    {
        String s1 = "CommandInput >> ";
        String s3 = s1 + val;
        xSemaphoreTake(mutex, 10);
        Serial.println(s3);
        xSemaphoreGive(mutex); 
    }
    else
    {
        String s1 = "Trig;";
        String s3 = s1 + val;
        xSemaphoreTake(mutex, 10);
        Serial.println(s3);
        xSemaphoreGive(mutex); 
    }
    xSemaphoreTake(mutex, 10);
    Serial.flush();
    xSemaphoreGive(mutex);
}


void handcheck()
{
  xSemaphoreTake(mutex, 10);
  if(digitalRead(Qx10[0]))
  {
    Serial.println("HandCheck;{\"StopMC\":true}");
  }
  else
  {
    Serial.println("HandCheck;{\"StopMC\":false}");
  }
  xSemaphoreGive(mutex); 
}

void initialDisp()
{

    display.display();
    delay(200);
    display.clearDisplay();
    display.setTextSize(1); // Draw 2X-scale text
    display.setTextColor(SSD1306_WHITE);

    display.setCursor(0, 0);
    display.fillRect(0, 0, display.width(), 12, SSD1306_INVERSE);
    display.display(); // Update screen with each newly-drawn rectangle

    display.setTextColor(SSD1306_BLACK);
    display.setCursor(4, 2);
    display.println("ESEC Anormaly Detect");
    display.display();

    dispIP();

    dispMAC();

    dispMCID();

    dispRate();
    
}

void dispRate()
{
    display.setTextColor(WHITE,BLACK);
    display.setCursor(0, 49);
    display.print("Rate ");
    display.print(Rate);
    display.println(" mS   ");
    display.display();
}

void dispMCID()
{
    display.setTextColor(WHITE,BLACK);
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
    display.setTextColor(WHITE,BLACK);
    display.setCursor(0, 27);
    display.println("                        ");
    display.display();
    display.setCursor(0, 27);
    display.print("MAC ");
    display.println(MAC);
    display.display();
}

void dispIP()
{
    display.setTextColor(WHITE,BLACK);
    display.setCursor(0, 16);
    display.println("                      ");
    display.display();
    display.setCursor(0, 16);
    display.print("IP ");
    display.print(IP);
    display.println("    ");
    display.display();
}
