#ifndef CONFIG_H
#define CONFIG_H

#include <stdio.h>

#include "stringlist.h"
#include "message.h"
#include "dict.h"


typedef struct BareConfigStruct BareConfigStruct;

BareConfigStruct *bareConfigCreate(MessageStruct *m, FILE *outFd, FILE *inFd, FILE *errFd);

/*
 * FIXME : could the Python lib work the same way ?
 */

const char *ConfigGetDefaultValue(BareConfigStruct *cfg, const char*);
const char *ConfigGetOptionValue(BareConfigStruct *cfg, const char *opt);
int 		ConfigSetOptionValue(BareConfigStruct *cfg, const char*, const char*);
void 	ConfigFree(BareConfigStruct*);

BareConfigStruct *optionConfigCreate(Dict *options, Dict *defaults);
int optionConfigUpdateDefaults(BareConfigStruct *cfg, Dict *opt);
int optionConfigUpdateOptions(BareConfigStruct *cfg, Dict *opt);

#endif
