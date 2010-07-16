#include "stringlist.h"

struct StringList
{
	char **list;
	unsigned int count;
};

StringList* stringListCreate(size_t len)
{
	StringList *ret = malloc(sizeof(StringList));
	ret->count = len;
	ret->list = malloc(sizeof(char*) * len);

	return ret;
}

int stringListInsertAt(StringList *l, unsigned int pos, const char *str)
{
	if(!l || !l->list || l->count < pos)
		return 0;
	
	l->list[pos] = str;

	return 1;
}

unsigned int stringListCount(StringList *l)
{
	if (!l)
		return 0;
	return l->count;
}

char* stringListGetAt(StringList *l, unsigned int pos)
{
	if (!l || !l->list || pos >= l->count)
		return NULL;
	
	return l->list[pos];
}

StringList* listToCList(PyObject* list)
{
	if (!list || !PyList_Check(list))
		return NULL;

	unsigned int len = PyList_Size(list);
	StringList *ret = malloc(sizeof(StringList));
	ret->count = len;
	ret->list = malloc(sizeof(char*) * len);

	for (unsigned int i = 0; i < len; i++)
	{
		PyObject *elem = PyList_GetItem(list, i);
		ret->list[i] = malloc(sizeof(char) * (PyBytes_Size(elem) + 1));
		strcpy(ret->list[i], PyBytes_AsString(elem));
	}

	return ret;
}

PyObject* cListToPyList(StringList* list)
{
	if (!list)
		Py_RETURN_NONE;

	PyObject *ret = PyList_New(list->count);
	for(unsigned int i = 0; i < list->count; i++)
	{
		PyList_SetItem(ret, i, PyBytes_FromString(list->list[i]));
	}

	return ret;
}

void stringListPrint(StringList* list)
{
	if (!list)
		return;

	for(unsigned int i = 0; i < list->count; i++)
	{
		printf("\"%s\"", list->list[i]);
		if (i < list->count - 1)
			printf(", ");
	}
}

void stringListFree(StringList* list)
{
	if (!list)
		return;

	if (list && list->list)
	{
		for(unsigned int i = 0; i < list->count; i++)
		{
			free(list->list[i]);
		}

		free(list->list);
	}

	if (list)
		free(list);
}

