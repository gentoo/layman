#include "stringlist.h"

struct StringList
{
	char **list;
	int count;
};

StringList* stringListCreate(size_t count)
{
	return NULL;
}

StringList* listToCList(PyObject* list)
{
	if (!list || !PyList_Check(list))
		return NULL;

	int len = PyList_Size(list);
	StringList *ret = malloc(sizeof(StringList));
	ret->count = len;
	ret->list = malloc(sizeof(char*) * len);

	for (int i = 0; i < len; i++)
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
	for(int i = 0; i < list->count; i++)
	{
		PyList_Append(ret, PyBytes_FromString(list->list[i]));
	}

	return ret;
}

void stringListPrint(StringList* list)
{
	if (!list)
		return;

	for(int i = 0; i < list->count; i++)
	{
		printf("\"%s\"", list->list[i]);
		if (i < list->count - 1)
			printf(", ");
	}

	free(list);
}

void stringListFree(StringList* list)
{
	if (!list)
		return;

	for(int i = 0; i < list->count; i++)
	{
		free(list->list[i]);
	}

	free(list);
}

