#ifndef DB_BASE_H
#define DB_BASE_H

#include "config.h"
#include "dict.h"

typedef struct DbBase DbBase;

DbBase* createDbBase(const char *paths[], unsigned int path_count, Dict *c, int ignore, int quiet, int ignore_init_read_errors);

#endif
