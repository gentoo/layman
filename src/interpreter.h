#ifndef INTERPRETER_H
#define INTERPRETER_H

#include <Python.h>

void 		interpreterInit();
void 		interpreterFinalize();
PyObject*	executeFunction(const char *module, const char *funcName, const char* format, ...);

#endif
