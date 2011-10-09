#include <Python.h>
#include <stdio.h>

#include "config.h"
#include "internal.h"
#include "dict.h"
#include "basic.h"


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
struct BareConfigStruct
{
	PyObject *object;
}

/**
 * \internal
 * Returns the internal Python object.
 */
PyObject *
_ConfigObject(BareConfigStruct *c)
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
 * \return a new instance of a BareConfigStruct object. It must be freed with bareConfigFree()
 */
BareConfigStruct *
bareConfigCreate(MessageStruct *m, FILE *outFd, FILE *inFd, FILE *errFd)
{
	if(!m)
		return NULL;
	
	if (!outFd || fileno(outFd) <= 0)
		outFd = stdout;
	if (!inFd || fileno(inFd) <= 0)
		inFd = stdin;
	if (!errFd || fileno(errFd) <= 0)
		errFd = stderr;
	
	PyObject *pyout = PyFile_FromFile(outFd, "", "w", 0); 
	PyObject *pyin = PyFile_FromFile(inFd, "", "r", 0);
	PyObject *pyerr = PyFile_FromFile(errFd, "", "w", 0);

	PyObject *obj = executeFunction("layman.config", "BareConfig", "OOOO", _messagePyObject(m), pyout, pyin, pyerr);
	Py_DECREF(pyout);
	Py_DECREF(pyin);
	Py_DECREF(pyerr);

	if (!obj)
	{
		debug("The execution failed, Are you sure >=app-portage/layman-2.0* is properly installed ?\n");
		return NULL;
	}

	BareConfigStruct *ret = malloc(sizeof(BareConfigStruct));
	ret->object = obj;

	return ret;
}


/**
 * Frees a BareConfigStruct object.
 */
void 
ConfigFree(BareConfigStruct *cfg)
{
	if (cfg && cfg->object)
	{
		Py_DECREF(cfg->object);
	}

	if (cfg)
	{
		free(cfg);
		cfg = NULL;
	}
}


/**
 * Get an option's default value.
 *
 * \param opt the name of the option
 * 
 * \return the value or NULL on failure.
 */
const char *
ConfigGetDefaultValue(BareConfigStruct *cfg, const char *opt)
{
	PyObject *obj = PyObject_CallMethod(_ConfigObject(cfg), "get_defaults", NULL);
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


/**
 * Get an option's current value.
 *
 * \param opt the name of the option
 *
 * \return the value or NULL on failure
 */
const char *
ConfigGetOptionValue(BareConfigStruct *cfg, const char *opt)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "get_option", "(z)", opt);
	char *tmp = PyString_AsString(obj);
	char *ret = malloc(sizeof(char) * (strlen(tmp) + 1));

	strcpy(ret, tmp);

	Py_DECREF(obj);

	return ret;
}


/**
 * Modifies an option's value
 *
 * \param opt the name of the option
 * \param val the new value for this option
 *
 * \return True on success, 0 on failure
 */
int 
ConfigSetOptionValue(BareConfigStruct *cfg, const char *opt, const char *val)
{
	PyObject *obj = PyObject_CallMethod(cfg->object, "set_option", "(zz)", opt, val);
	int ret;
	if (obj)
		ret = True;
	else
		ret = False;
	
	Py_DECREF(obj);

	return ret;
}


/**
 * Creates an option config object with new option and/or default values.
 *
  *
 * \return a new instance of a OptionConfig object. It must be freed with ConfigFree()
 */
BareConfigStruct *
optionConfigCreate( Dict *options, Dict *defaults)
{

	PyObject *opts = dictToPyDict(options);
	PyObject *dflts = dictToPyDict(defaults);
	PyObject *obj = executeFunction("layman.config", "OptionConfig", "OOOO", opts, dflts);

	if (!obj)
	{
		debug("The execution failed, Are you sure >=app-portage/layman-2.0* is properly installed ?\n");
		return NULL;
	}

	BareConfigStruct *ret = malloc(sizeof(BareConfigStruct));
	ret->object = obj;
	
	Py_DECREF(opts);
	Py_DECREF(dflts);

	return ret;
}


/**
 * Updates the options values
 *
 * \param opt Dict of the key/value pairs
  *
 * \return True on success, False on failure
 */
int 
optionConfigUpdateOptions(BareConfigStruct *cfg, Dict *opt)
{
	PyObject *opts = dictToPyDict(opt);
	PyObject *obj = PyObject_CallMethod(cfg->object, "update", "(zz)", opts);
	int ret;
	if (obj)
		ret = True;
	else
		ret = False;
	
	Py_DECREF(obj);
	Py_DECREF(opt);

	return ret;
}


/**
 * Updates the defaults values
 *
* \param opt Dict of the default key/value pairs
  *
 * \return True on success, 0 on failure
 */
int 
optionConfigUpdateDefaults(BareConfigStruct *cfg, Dict *opt)
{
	PyObject *opts = dictToPyDict(opt);
	PyObject *obj = PyObject_CallMethod(cfg->object, "update_defaults", "(zz)", opts);
	int ret;
	if (obj)
		ret = True;
	else
		ret = False;
	
	Py_DECREF(obj);
	Py_DECREF(opt);

	return ret;
}


/** @} */
