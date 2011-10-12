#ifndef INTERPRETER_H
#define INTERPRETER_H

 
/**  High level interactive python session structure */
typedef struct PythonSessionStruct
{
	// variables
	PythonInterpreter interpreter;
	
	// Functions
	
	static void Finalize(PythonSessionStruct *session)
} PythonSessionStruct;


PythonSessionStruct PySession();

#endif
