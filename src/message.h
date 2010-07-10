#ifndef MESSAGE_H
#define MESSAGE_H

#include <Python.h>
#include "stringlist.h"

typedef struct Message Message;

/*
 * arguments : module (String), stdout (fd), stderr (fd), stderr (fd), debug_level, debug_verbosity, info_level, warn_level, ?, ?, ?, ?
 */
Message *messageCreate(const char*, FILE*, FILE*, FILE*, int, int, int, int, int, StringList*, StringList*, StringList*);
PyObject *_messageObject(Message* m);

#endif
