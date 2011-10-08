#ifndef DICT_H
#define DICT_H

typedef struct Dict Dict;

Dict *dictCreate();
//char*		tableFind(Dict *table, char* key);
void		dictFree(Dict *t);
void		dictInsert(Dict *list, const char *key, const char *value);
unsigned int	dictCount(Dict *table);
 
#endif
