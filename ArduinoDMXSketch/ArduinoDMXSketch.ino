/* This program allows you to set DMX channels over the serial port.
**
** After uploading to Arduino, switch to Serial Monitor and set the baud rate
** to 9600. You can then set DMX channels using these commands:
**
** <number>c : Select DMX channel
** <number>v : Set DMX channel to new value
**
** These can be combined. For example:
** 100c355w : Set channel 100 to value 255.
**
** For more details, and compatible Processing sketch,
** visit http://code.google.com/p/tinkerit/wiki/SerialToDmx
**
** Help and support: http://groups.google.com/group/DmxMaster */

#include <DmxMaster.h>


void setup() {
  Serial.begin(9600);
  Serial.println("SerialToDmx ready");
  Serial.println();
  Serial.println("Syntax:");
  Serial.println(" 123c : use DMX channel 123");
  Serial.println(" 45w : set current channel to value 45");
  Serial.println(" 123cg : Get level of channel ");
}

int value = 0;
int channel;
int fade ;
int level ;

/*variables for fading*/
unsigned long fadeNextUpdateTime = 0;
unsigned long fadeInfo[10][5] ; //{ channel, finalval,steps, fadeinterval, netxstep, }, 


void loop() {
  int c;
  if(Serial.available()){
  c = Serial.read();
  if ((c>='0') && (c<='9')) {
    value = 10*value + c - '0';
  } else {
    if (c=='c') {
        channel = value;
            //stop fade for channel if already in progress
            int i = 0 ;
            for (i = 0; i < 10; i = i + 1) {
               if (fadeInfo[i][0] == channel){
                    fadeInfo[i][2]=0;
               }
             }
             
        value = 0;
    }else if (c=='f') { 
        fade = value;
        value = 0;
    }else if (c=='g') { 
           Serial.print(channel);
           Serial.print("c");
           Serial.print(DmxMaster.getValue(channel));
           Serial.println("l");
    }else if (c=='w') {
            level = value;
            value = 0;
      if(fade==0) {
           DmxMaster.write(channel, level);
           Serial.print(channel);
           Serial.print("c");
           Serial.print(DmxMaster.getValue(channel));
           Serial.println("l");
      
       } else { 
            
         // Find availble fade array
          int i = 0 ;
          for (i = 0; i < 10; i = i + 1) {
            if (fadeInfo[i][2]==0){
                  fadeInfo[i][0]=channel;
                  fadeInfo[i][1]=level;
                  int steps= DmxMaster.getValue(channel) - level;
                  fadeInfo[i][2]= abs(steps);
                  fadeInfo[i][3]=(fade*1000)/fadeInfo[i][2] ; //getinterval in millisseconds
                  fadeInfo[i][4]=millis()+fadeInfo[i][3];
        
                  //reset fade to default
                   fade=0;
                   
                  //found a place to store don't check remaing
                  i = 11;
            }
          }
          if (i==10){ //all fade slots are full, immediately write change
                   DmxMaster.write(channel, level);
                   Serial.print(channel);
                   Serial.print("c");
                   Serial.print(DmxMaster.getValue(channel));
                   Serial.println("l");
           }
         
        }

           
  }
       
  }
  }
  updateFades();
}


void updateFades(){
    /*Check for fade job and fade as needed */
  if (fadeNextUpdateTime < millis()) {
    int i=0;  
    for (i = 0; i < 9; i = i + 1) {
            if (fadeInfo[i][2]>0){
                if (millis()> fadeInfo[i][4]){
                   //Serial.println("Fading");
                  fadeInfo[i][2]= fadeInfo[i][2] -1;
                  fadeInfo[i][4]=millis()+fadeInfo[i][3];
                     if(fadeInfo[i][1] < DmxMaster.getValue(fadeInfo[i][0])){
                        DmxMaster.write(fadeInfo[i][0], (DmxMaster.getValue(fadeInfo[i][0])-1));
                      }else{
                        DmxMaster.write(fadeInfo[i][0], (DmxMaster.getValue(fadeInfo[i][0])+1));
                      }
                      if ( fadeInfo[i][2] == 0){
                        //once get to final print value
                          Serial.print(fadeInfo[i][0]);
                          Serial.print("c");
                          Serial.print(DmxMaster.getValue(fadeInfo[i][0]));
                          Serial.println("l");  
                      }
              }
       }
    }
     
    fadeNextUpdateTime = 5 + millis();
     
  }
}
