/* ---------------------------------------------------------------------------*
 * A simple implementation of tool coupling type FMU
 *
 * Copyright (c) 2016, Amane Tanaka
 *
 *  03.08.2016 initial vaersion
 * ---------------------------------------------------------------------------*/

#include "model.h" 
#include "fmuTemplate.h"

// define initial state vector as vector of value references
#define STATES { h_, v_ }
#define BUFFER_SIZE 512

char itemName[NUMBER_OF_ITEMS][32];
char itemValue[NUMBER_OF_ITEMS][256];
char inputName[NUMBER_OF_REAL_INPUTS][32];
char outputName[NUMBER_OF_REAL_OUTPUTS][32];
double inputValue[NUMBER_OF_REAL_INPUTS];
double outputValue[NUMBER_OF_REAL_OUTPUTS];
int n_offset = NUMBER_OF_REAL_INPUTS;

int socket1;
struct sockaddr_in addr1;
char buffer1[BUFFER_SIZE];
int socket2;
struct sockaddr_in addr2;
char buffer2[BUFFER_SIZE];
char destination[32];
WSADATA wsadata;
	
#include "variables.c"

// connect to server using socket1
int linkConnect1(){
	memset(&addr1, 0, sizeof(addr1));
	addr1.sin_port = htons(PORT);
	addr1.sin_family = AF_INET;
	addr1.sin_addr.s_addr = inet_addr(IPADDR);
	socket1 = socket(AF_INET, SOCK_STREAM, 0);
	if(connect(socket1, (struct sockaddr *) &addr1, sizeof(addr1))){
		return(-1);
	}else{
		return(1);
	}
 }
 
 // connect to server using socket2
int linkConnect2(){
	memset(&addr2, 0, sizeof(addr2));
	addr2.sin_port = htons(PORT);
	addr2.sin_family = AF_INET;
	addr2.sin_addr.s_addr = inet_addr(IPADDR);
	socket2 = socket(AF_INET, SOCK_STREAM, 0);
	if(connect(socket2, (struct sockaddr *) &addr2, sizeof(addr2))){
		return(-1);
	}else{
		return(1);
	}
 }
 
 // send and recive message
 void linkComm1(char *smes){
		memset(buffer1,0,sizeof(buffer1));
		strcpy(buffer1, smes);
		send(socket1, buffer1, BUFFER_SIZE, 0);
		memset(buffer1,0,sizeof(buffer1));
		recv(socket1, buffer1, BUFFER_SIZE, 0);
} 

// send and recive message
 void linkComm2(char *smes){
		memset(buffer2,0,sizeof(buffer2));
		strcpy(buffer2, smes);
		send(socket2, buffer2, BUFFER_SIZE, 0);
		memset(buffer2,0,sizeof(buffer2));
		recv(socket2, buffer2, BUFFER_SIZE, 0);
} 

// send message
void linkSend1(char *smes){
		memset(buffer1,0,sizeof(buffer1));
		strcpy(buffer1, smes);
		send(socket1, buffer1, BUFFER_SIZE, 0);	
}

void linkClose1(){
	closesocket(socket1);
}

void linkClose2(){
	closesocket(socket2);
}


int linkInstantiate(){
	char smes[128];
	int i;
	
	linkComm1("instantiate");
	// send model items & values
	memset(smes,0,sizeof(smes));
	sprintf(smes, "%d", NUMBER_OF_ITEMS);
	linkComm1(smes);
	for (i = 0; i < NUMBER_OF_ITEMS; i++){
		linkComm1(itemName[i]);
		linkComm1(itemValue[i]);
	}
	// send input variables 
	memset(smes,0,sizeof(smes));
	sprintf(smes, "%d", NUMBER_OF_REAL_INPUTS);
	linkComm1(smes);
	for (i = 0; i < NUMBER_OF_REAL_INPUTS; i++){
		linkComm1(inputName[i]);
		memset(smes,0,sizeof(smes));
		sprintf(smes,"%lf",inputValue[i]);
		linkComm1(smes);
	}
	// send output variables
	memset(smes,0,sizeof(smes));
	sprintf(smes, "%d", NUMBER_OF_REAL_OUTPUTS);
	linkComm1(smes);
	for (i = 0; i < NUMBER_OF_REAL_OUTPUTS; i++){
		linkComm1(outputName[i]);
		memset(smes,0,sizeof(smes));
		sprintf(smes,"%g",outputValue[i]);
		linkComm1(smes);
	}
	linkComm1("initialize");
	return(1);
}

int linkDoStep(double ct, double cstep){
	char smes[128];
	int i;

	// send current comunicatin point and comunication step
	linkComm1("dostep");
	
	// send comunication point and comunication step
	memset(smes,0,sizeof(smes));
	sprintf(smes,"%g",ct);
	linkComm1(smes);
	memset(smes,0,sizeof(smes));
	sprintf(smes,"%g",cstep);
	linkComm1(smes);
	
	// send input data
	for (i=0; i < NUMBER_OF_REAL_INPUTS; i++){
		memset(smes,0,sizeof(smes));
		sprintf(smes,"%g",inputValue[i]);
		linkComm1(smes);
	}	
	linkComm1("wait");
	// recieve output data
	for (i=0;i < NUMBER_OF_REAL_OUTPUTS; i++){
		linkComm1("out");
		sscanf(buffer1,"%lf",&outputValue[i]);
		printf("output[%d]=%g",i, outputValue[i]);
	}
	return(1);
}

int linkTerminate(){
	if (linkConnect2()==1){
		linkComm2("terminate");
		linkClose1();
		linkClose2();
		return(1);
	}else{
		return(-1);
	}
}

void linkFree(){
	WSACleanup();	
}

// called by fmiInstantiateModel
void setStartValues(ModelInstance *comp) {
	int i;
	sprintf(destination, "%s", IPADDR);
	defineVariables();
	for (i=0; i < NUMBER_OF_REAL_INPUTS; i++){
		r(i) = inputValue[i];
	}
	for (i=0; i < NUMBER_OF_REAL_OUTPUTS; i++){
		r(n_offset + i) = outputValue[i];
	}
	WSAStartup(MAKEWORD(2,0), &wsadata);	
}

// called by fmiGetReal, fmiGetContinuousStates and fmiGetDerivatives
fmiReal getReal(ModelInstance* comp, fmiValueReference vr){
	if (vr < NUMBER_OF_REALS){
		return r(vr);
	}else{
		return 0.0;
	}
}

// called by fmiInitialize()
void initialize(ModelInstance* comp, fmiEventInfo* eventInfo) {
 	if ( linkConnect1() == 1){
		if ( linkInstantiate() ==1){
	
		}
	}
}

fmiReal getEventIndicator(ModelInstance* comp, int z) {
	return 0;
}

#include "fmuTemplate_.c"
