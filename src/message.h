#ifndef MESSAGE_H
#define MESSAGE_H

#include <stdio.h>
#include "stringlist.h"

typedef struct Message Message;

Message*	messageCreate(const char* module, FILE* out, FILE* err, FILE* dbg);
void		messageFree(Message *m);

#endif
