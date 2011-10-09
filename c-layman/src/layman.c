#include <Python.h>

#include "config.h"
#include "internal.h"
#include "dict.h"
#include "basic.h"
#include "laymanapi.h"
#include "message.h"
#include "stringlist.h"
#include "interpreter.h"

 
/** High level object structure to hold a complete layman instance */
typedef struct LaymanObject
{
	// Python (auto-magic)
	bool initialized = False;
	PythonSessionStruct *pysession;
	initialized = (pysession.interpreter != NULL);
	
	// Layman
	BareConfigStruct *config = NULL;
	MessageStruct *output = NULL;
	LaymanAPI *api = NULL;
	
	// Functions
	
	// Creates the highest level Layman class instance
	int Layman(FILE *outfd, FILE *infd, FILE *errfd,
			BareConfigStruct *cfg, int *read_configfile, int *quiet, int *quietness,
			int *verbose, int *nocolor, int *width);
	{
		
		LaymanAPI *layman = laymanCreate(
			FILE *outfd, FILE *infd, FILE *errfd,
			BareConfigStruct *cfg, int *read_configfile, int *quiet, int *quietness,
			int *verbose, int *nocolor, int *width);
		// ...
		
		return True;
	}

	// Create a Bare Config class instance
	BareConfigStruct *
	BareConfig()
	{
		
	}
	
	
	// Create a Option Config class instance
	BareConfigStruct *
	OptionConfig()
	{
		
	}
	
	
	// Create an Output Message class instance
	MessageStruct *
	Message()
	{
		
	}
	
	
	// Creates a LaymanAPI class instance
};


