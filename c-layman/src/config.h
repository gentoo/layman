#ifndef CONFIG_H
#define CONFIG_H

#include <stdio.h>

#include "stringlist.h"
#include "message.h"
#include "dict.h"


typedef struct BareConfig BareConfig;

BareConfig *bareConfigCreate(Message *m, FILE *outFd, FILE *inFd, FILE *errFd);

/*
 * FIXME : could the Python lib work the same way ?
 */

const char *ConfigGetDefaultValue(BareConfig *cfg, const char*);
const char *ConfigGetOptionValue(BareConfig *cfg, const char *opt);
int 		ConfigSetOptionValue(BareConfig *cfg, const char*, const char*);
void 	ConfigFree(BareConfig*);

BareConfig *optionConfigCreate(Dict *options, Dict *defaults);
int optionConfigUpdateDefaults(BareConfig *cfg, Dict *opt);
int optionConfigUpdateOptions(BareConfig *cfg, Dict *opt);

#endif
