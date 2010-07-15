#ifndef CONFIG_H
#define CONFIG_H

#include <Python.h>

#include "stringlist.h"
#include "message.h"

typedef struct BareConfig BareConfig;

BareConfig*	bareConfigCreate(Message* m, FILE* outFd, FILE* inFd, FILE* errFd);

/*
 * FIXME : could the Python lib work the same way ?
 */

const char*	bareConfigGetDefaultValue(BareConfig* cfg, const char*);
const char*	bareConfigGetOptionValue(BareConfig* cfg, const char* opt);
int 		bareConfigSetOptionValue(BareConfig* cfg, const char*, const char*);
PyObject* 	_bareConfigObject(BareConfig*);
void 		bareConfigFree(BareConfig*);

#endif
