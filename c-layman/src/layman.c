#include <Python.h>
// temp workaround for my environment
// since at times it fails to find Python.h
#include <python2.6/Python.h>

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
	// Python session placeholder
	bool pyinitialized = False;
	PythonSessionStruct *pysession;
	
	// Layman, placeholders for our primary modules
	BareConfigStruct *config = NULL;
	MessageStruct *output = NULL;
	LaymanAPI *api = NULL;
	bool initialized = False;
	// Functions
	
	/** Creates the highest level Layman class instance,
	* the config will default if not passed in.
	* the message class is automatic.
	*/
	static int (* Layman) (FILE *outfd, FILE *infd, FILE *errfd,
			BareConfigStruct *cfg, int *read_configfile, int *quiet, int *quietness,
			int *verbose, int *nocolor, int *width);

	/** Create a Bare Config class instance
	* edit the options as desired.
	*/
	static BareConfigStruct (* BareConfig) (MessageStruct *m, FILE *outFd, FILE *inFd, FILE *errFd);
	
	/** Create an Option Config class instance
	* pass in the options and default overrides in
	* as desired.
	*/
	static BareConfigStruct (* OptionConfig) (Dict *options, Dict *defaults);
	
	/** Create an Output Message class instance
	*/
	static MessageStruct (* Message) (FILE *out, FILE *err, int infolevel, int warnlevel, int col);
	
	/** Creates a LaymanAPI class instance
	*/
	static laymanAPI (* LaymanAPI) (FILE *outfd, FILE *infd, FILE *errfd,
		BareConfigStruct *cfg, int *read_configfile, int *quiet, int *quietness,
		int *verbose, int *nocolor, int *width);
		
};


static LaymanObject
Layman_session_create()
{
	LaymanObject *layman_session = malloc(sizeof(LaymanObject));
	
	PythonSessionStruct *pysession = PySession_create();
	layman_session->pysession = pysession;
	layman_session->pyinitialized = (pysession.interpreter != NULL);
	
	// now assign the function pointers
	assign_api_functions(layman_session);

	return layman_session;
}
