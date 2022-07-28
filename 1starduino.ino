#include "SPI.h"
#include "MFRC522.h"
#include <Servo.h>


#define SS_PIN 10
#define RST_PIN 9

Servo myservo1;
Servo myservo2;

MFRC522 rfid(SS_PIN ,RST_PIN);

MFRC522::MIFARE_Key key;

int slot1 = 0;
int slot2 = 0;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  pinMode(2,OUTPUT);
  pinMode(3,INPUT);
  pinMode(4,OUTPUT);
  pinMode(7,INPUT);
  myservo1.attach(8);
  myservo2.attach(6);
  myservo1.write(0);
  myservo2.write(0);
  spacedetect();
}

void loop() {

  
  while(Serial.available()==0)
  {
  if(!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial())

    return;

  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

  if(piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
     piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
     piccType != MFRC522::PICC_TYPE_MIFARE_4K)

     {
      Serial.println(F("YOUR TAG IS NOT OF TYPE MIFARE CLASSIC."));
      return;
     }
      String strID = "";
      
  for (byte i = 0; i < 4; i++) {
    strID +=
      (rfid.uid.uidByte[i] < 0x10 ? "0" : "") +
      String(rfid.uid.uidByte[i], HEX) +
      (i != 3 ? ":" : "");
  }
  strID.toUpperCase();
  delay(1000);
  Serial.println(strID);
  String indataser = Serial.readString();
  indataser.trim();
  checkInp(indataser);
  }
      
}

void spacedetect()
{
  digitalWrite(2,LOW);
  digitalWrite(2,HIGH);
  delayMicroseconds(10);
  digitalWrite(2, LOW);
  float dur1 = pulseIn(3, HIGH);
  float dis1 = (dur1 * 0.0343)/2;
  digitalWrite(4,LOW);
  digitalWrite(4,HIGH);
  delayMicroseconds(10);
  digitalWrite(4, LOW);
  float dur2 = pulseIn(7, HIGH);
  float dis2 = (dur2 * 0.0343)/2;
  Serial.println(dis1);
  Serial.println(dis2);
  if (dis1 <= 10 && dis2 <= 10)
  {
    slot1 = 1;
    slot2 = 1;
    Serial.println("Both slots are full");
    delay(1000); 
  }
  else if (dis1 <= 10)
  {
    slot1 = 1;
    Serial.println("SLOT 1 is full");
    delay(1000);
  }
  else if (dis2 <= 10)
  {
    slot2 = 1;
    Serial.println("SLOT 2 is full");
    delay(1000);
  }
  else
  {
    slot1 = 0;
    slot2 = 0;
    Serial.println("Both slots are empty"); 
    delay(1000);
  }
}
void openGate(int gateNo)
{
  if(gateNo == 1)
  {
    myservo1.write(120);
    //Serial.println("khul gaya bhai 1"); 
    while(true)
    {
    int p = analogRead(A0);
    //Serial.println(p); 
    if(p>=500)
    {
      myservo1.write(0);
      Serial.println("band kar de bhai gate 1 ho gaya");
      break;
    }
    }
    }

  else if(gateNo == 2)
  {
    myservo2.write(120);
    //Serial.println("khul gaya bhai 2"); 
    while(true)
    {
    int p = analogRead(A1);
    //Serial.println(p); 
    if(p>=500)
    {
      myservo2.write(0);
      Serial.println("band kar de bhai gate 2 ho gaya");
      break;
    }
    }
    
  }
 
}


void checkInp(String indata)
{
      if(indata.equals("space check"))
      {
        spacedetect();
      }

      else if(indata.equals("open gate 1"))
      {
        openGate(1);
      }
      else if(indata.equals("open gate 2"))
      {
        openGate(2);
      }
  
  }
