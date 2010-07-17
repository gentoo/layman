#ifndef STRINGLIST_H
#define STRINGLIST_H

#include <sys/types.h>

typedef struct StringList StringList;

StringList*	stringListCreate(size_t);
unsigned int	stringListCount(StringList*);
int		stringListInsertAt(StringList*, unsigned int, char*);
char*		stringListGetAt(StringList*, unsigned int);
void		stringListPrint(StringList*);
void		stringListFree(StringList*);

#endif
