#include <Python.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[])
{
	PyObject *pP1, *pP2, *pArgs, *pName, *pModule, *pDict, *pFunc, *pValue;

	Py_Initialize();

	//printf("%s\n", Py_GetVersion());

	//pName = PyByteArray_FromStringAndSize("portage", strlen("portage"));
	pModule = PyModule_New("portage");

	pDict = PyModule_GetDict(pModule);
	pFunc = PyDict_GetItemString(pDict, "pkgcmp");

	if (PyCallable_Check(pFunc)) 
	{
		pP1 = PyByteArray_FromStringAndSize("app-portage/kuroo4-4.2", strlen("app-portage/kuroo4-4.2"));
		pP2 = PyByteArray_FromStringAndSize("app-portage/kuroo4-4.3", strlen("app-portage/kuroo4-4.3"));

		pArgs = PyTuple_New(2);

		PyTuple_SetItem(pArgs, 0, pP1);	
		PyTuple_SetItem(pArgs, 0, pP2);	

		pValue = PyObject_CallObject(pFunc, pArgs);

		if (pArgs != NULL)
		{
			Py_DECREF(pArgs);
		}
	}
	else 
		PyErr_Print();

	int ret = PyLong_AsLong(pValue);
	switch(ret)
	{
	case -1:
		printf("less");
		break;
	case 0:
		printf("same");
		break;
	case 1:
		printf("more");
		break;
	}

	printf("\n");

	Py_DECREF(pModule);

	Py_Finalize();
}
