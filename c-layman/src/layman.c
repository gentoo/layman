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
	// Python
	bool initialized = False;
	PythonSessionStruct *pysession;
	initialized = assert(pysession.initialized);
	
	// Layman
	BareConfig *config = NULL;
	Message *output = NULL;
	LaymanAPI *api = NULL;
	
	
};


