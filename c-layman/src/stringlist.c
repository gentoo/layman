#include <Python.h>
#include <stdlib.h>
#include "stringlist.h"

/** \defgroup string_list StringList
 * \brief String list management class
 */

/** \addtogroup string_list
 * @{
 */
struct StringList
{
	char **list;
	unsigned int count;
};

/**
 * Creates a String list to use with the library.
 * \param len the number of strings in the list.
 */
StringList* stringListCreate(size_t len)
{
	StringList *ret = malloc(sizeof(StringList));
	ret->count = len;
	ret->list = malloc(sizeof(char*) * len);

	return ret;
}

/**
 * Inserts the string str in the list l at position pos.
 * \return True if it succeeded, False if not.
 */
int stringListInsertAt(StringList *l, unsigned int pos, char *str)
{
	if(!l || !l->list || l->count < pos)
		return 0;
	
	l->list[pos] = str;

	return 1;
}

/**
 * Get the number of strings in the list.
 *
 * \return the number of strings in the list
 */
unsigned int stringListCount(StringList *l)
{
	if (!l)
		return 0;
	return l->count;
}

/**
 * Get the String at position pos
 * \return the String at position pos
 */
char* stringListGetAt(StringList *l, unsigned int pos)
{
	if (!l || !l->list || pos >= l->count)
		return NULL;
	
	return l->list[pos];
}

/**
 * \section internal
 * @{
 * \internal
 */

/**
 * Converts a Python list object to a C String list
 */
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
		//Item are copied so that the PyObject can be deleted after the call without
		//destroying the data in the returned list.
		PyObject *elem = PyList_GetItem(list, i);
		ret->list[i] = malloc(sizeof(char) * (PyBytes_Size(elem) + 1));
		strcpy(ret->list[i], PyBytes_AsString(elem));
	}

	return ret;
}

/**
 * Converts a C String list to a Python List object
 */
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

/** @} */

/**
 * Prints a C String list.
 */
void stringListPrint(StringList* list)
{
	if (!list)
		return;

	for(unsigned int i = 0; i < list->count; i++)
	{
		printf("\"%s\"", list->list[i]);
		// No coma after the last item.
		if (i < list->count - 1)
			printf(", ");
	}
}

/**
 * Frees a string list and it's data
 */
void stringListFree(StringList* list)
{
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

/** @} */
