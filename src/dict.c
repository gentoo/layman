#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dict.h"

/*
 * Dict
 */
typedef struct DictElem DictElem;
struct DictElem
{
	const char *key;
	const char *val;
	struct DictElem *next;
};

struct Dict
{
	DictElem *root;
	int count;
};

Dict *dictCreate()
{
	Dict *ret = malloc(sizeof(Dict));
	ret->count = 0;
	ret->root = 0;
	return ret;
}

void dictInsert(Dict* list, const char* key, const char* value)
{
	if (!list)
		return;
	DictElem *node = malloc(sizeof(DictElem));
	node->key = key;
	node->val = value;
	node->next = list->root;
	list->root = node;
	list->count++;
}

unsigned int dictCount(Dict *list)
{
	return (list ? list->count : 0);
}

void dictFree(Dict *list)
{
	if (!list)
		return;

	DictElem *node = list->root;
	while (node)
	{
		DictElem *tmp = node;
		node = node->next;
		free(tmp);
	}

	free(list);
}

PyObject *dictToPyDict(Dict *dict)
{
	PyObject *pydict = PyDict_New();
	DictElem *node = dict->root;
	while (node)
	{
		PyDict_SetItem(pydict, PyBytes_FromString(node->key), PyBytes_FromString(node->val));
		node = node->next;
	}

	return pydict;
}
