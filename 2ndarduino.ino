
void setup()
{
  Serial.begin(9600);
  pinMode(A0,INPUT);
  pinMode(2,OUTPUT);

}

void loop()
{
  checkLight();
}

void checkLight()
{
  int p = analogRead(A0);
  
  if(p<256)
  {
    digitalWrite(2,HIGH);
  }
  else
  {
    digitalWrite(2,LOW);
  }
}
