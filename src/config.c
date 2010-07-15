#include <Python.h>

#include "config.h"
#include "interpreter.h"

struct BareConfig
{
	PyObject *object;
};

PyObject *_bareConfigObject(BareConfig *c)
{
	if (c && c->object)
		return c->object;
	else
		Py_RETURN_NONE;
}

BareConfig *bareConfigCreate(Message *m, FILE* outFd, FILE* inFd, FILE* errFd)
{
	PyObject *pyout = PyFile_FromFile(((!outFd || fileno(outFd) <= 0) ? stdout : outFd),
				"", "w", 0);
	PyObject *pyin = PyFile_FromFile(((!inFd || fileno(inFd) <= 0) ? stdin : inFd),
				"", "r", 0);
	PyObject *pyerr = PyFile_FromFile(((!errFd || fileno(errFd) <= 0) ? stderr : errFd),
				"", "w", 0);

	PyObject *obj = executeFunction("layman.config", "BareConfig", "OOOO", _messageObject(m), pyout, pyin, pyerr);
	Py_DECREF(pyout);
	Py_DECREF(pyin);
	Py_DECREF(pyerr);

	if (!obj)
		return NULL;

	BareConfig *ret = malloc(sizeof(BareConfig));
	ret->object = obj;

	return ret;
}

void bareConfigFree(BareConfig* cfg)
{
	if (cfg && cfg->object)
	{
		Py_DECREF(cfg->object);
	}

	if (cfg)
		free(cfg);
}

const char* bareConfigGetDefaultValue(BareConfig* cfg, const char* opt)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "get_defaults", NULL);
	if (!obj)
		return NULL;

	if (PyDict_Contains(obj, PyBytes_FromString(opt)))
	{
		PyObject *pyopt = PyBytes_FromString(opt);
		char *tmp = PyBytes_AsString(PyDict_GetItem(obj, pyopt));
		Py_DECREF(pyopt);

		char *ret = malloc(sizeof(char) * strlen(tmp));
		strcpy(ret, tmp);
		Py_DECREF(obj);

		return ret;
	}
	else
		return "";
}

const char* bareConfigGetOptionValue(BareConfig* cfg, const char* opt)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "get_option", "(z)", opt);
	char *tmp = PyBytes_AsString(obj);
	char *ret = malloc(sizeof(char) * (strlen(tmp) + 1));

	strcpy(ret, tmp);

	Py_DECREF(obj);

	return ret;
}

int bareConfigSetOptionValue(BareConfig* cfg, const char* opt, const char* val)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "set_option", "(zz)", opt, val);
	int ret;
	if (obj)
		ret = 1;
	else
		ret = 0;
	
	Py_DECREF(obj);

	return ret;
}
