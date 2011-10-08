#ifndef MESSAGE_H
#define MESSAGE_H

#include <stdio.h>

#include "stringlist.h"

typedef struct Message Message;

Message *messageCreate(FILE *out, FILE *err, int infolevel, int warnlevel, int col);
void		messageFree(Message *m);
int messageSetDebugLevel(Message *m, int debug_level);
int messageSetInfoLevel(Message *m, int info_level);
int messageSetWarnLevel(Message *m, int warn_level);

 
#endif
