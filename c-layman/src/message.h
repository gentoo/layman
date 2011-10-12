#ifndef MESSAGE_H
#define MESSAGE_H

#include <stdio.h>

#include "stringlist.h"

typedef struct MessageStruct MessageStruct;

MessageStruct *messageCreate(PythonSessionStruct *_pysession, 
												FILE *out,
												FILE *err, 
												int infolevel, 
												int warnlevel, 
												int col);
void		messageFree(MessageStruct *m);
int messageSetDebugLevel(MessageStruct *m, int debug_level);
int messageSetInfoLevel(MessageStruct *m, int info_level);
int messageSetWarnLevel(MessageStruct *m, int warn_level);

 
#endif
