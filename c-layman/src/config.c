#include <Python.h>

#include "config.h"
#include "internal.h"

/**
 * \internal
 */
#define debug(x)	printf(x)

/** \defgroup config Config
 * \brief Layman library configuration module
 */

/** \addtogroup config
 * @{
 */


/**
 * \internal
 */
struct BareConfig
{
	PyObject *object;
};

/**
 * \internal
 * Returns the internal Python object.
 */
PyObject *_bareConfigObject(BareConfig *c)
{
	if (c && c->object)
		return c->object;
	else
		Py_RETURN_NONE;
}

/**
 * Creates a bare config object with default values.
 *
 * \param outFd where information must be written to
 * \param inFd where information must be read from
 * \param errFd where errors must be written to
 *
 * \return a new instance of a BareConfig object. It must be freed with bareConfigFree()
 */
BareConfig *bareConfigCreate(Message *m, FILE* outFd, FILE* inFd, FILE* errFd)
{
	if (!outFd || fileno(outFd) <= 0)
		outFd = stdout;
	if (!inFd || fileno(inFd) <= 0)
		inFd = stdin;
	if (!errFd || fileno(errFd) <= 0)
		errFd = stderr;
	
	PyObject *pyout = PyFile_FromFile(outFd, "", "w", 0);
	PyObject *pyin = PyFile_FromFile(inFd, "", "r", 0);
	PyObject *pyerr = PyFile_FromFile(errFd, "", "w", 0);

	PyObject *obj = executeFunction("layman.config", "BareConfig", "OOOO", _messageObject(m), pyout, pyin, pyerr);
	Py_DECREF(pyout);
	Py_DECREF(pyin);
	Py_DECREF(pyerr);

	if (!obj)
	{
		debug("The execution failed, Are you sure app-portage/layman-8888 is properly installed ?\n");
		return NULL;
	}

	BareConfig *ret = malloc(sizeof(BareConfig));
	ret->object = obj;

	return ret;
}

/**
 * Frees a BareConfig object.
 */
void bareConfigFree(BareConfig* cfg)
{
	if (cfg && cfg->object)
	{
		Py_DECREF(cfg->object);
	}

	if (cfg)
		free(cfg);
}

/**
 * Get an option's default value.
 *
 * \param opt the name of the option
 * 
 * \return the value or NULL on failure.
 */
const char* bareConfigGetDefaultValue(BareConfig* cfg, const char* opt)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "get_defaults", NULL);
	if (!obj)
		return NULL;

	if (PyDict_Contains(obj, PyString_FromString(opt)))
	{
		PyObject *pyopt = PyString_FromString(opt);
		char *tmp = PyString_AsString(PyDict_GetItem(obj, pyopt));
		Py_DECREF(pyopt);

		char *ret = malloc(sizeof(char) * strlen(tmp));
		strcpy(ret, tmp);
		Py_DECREF(obj);

		return ret;
	}
	else
		return "";
}

/*
 * Get an option's current value.
 *
 * \param opt the name of the option
 *
 * \return the value or NULL on failure
 */
const char* bareConfigGetOptionValue(BareConfig* cfg, const char* opt)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "get_option", "(z)", opt);
	char *tmp = PyString_AsString(obj);
	char *ret = malloc(sizeof(char) * (strlen(tmp) + 1));

	strcpy(ret, tmp);

	Py_DECREF(obj);

	return ret;
}

/*
 * Modifies an option's value
 *
 * \param opt the name of the option
 * \param val the new value for this option
 *
 * \return True on success, 0 on failure
 */
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

/** @} */
