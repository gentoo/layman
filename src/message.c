#include <Python.h>
#include "message.h"
#include "internal.h"

struct Message
{
	PyObject *object;
};

/**
 * Creates a Message instance with default values.
 * To modify those values, use the corresponding functions.
 *
 * \param module the module to debug. If you don't know, set "layman"
 * \param out where to write info
 * \param err where to write errors
 * \param dbg where to write debug information
 *
 * \return a new instance of a Message object. It must be freed with messageFree()
 */
Message *messageCreate(const char* module,
			FILE* out,
			FILE* err,
			FILE* dbg)
{
	PyObject *pyout, *pyerr, *pydbg;

	if (!out || fileno(out) <= 0)
		out = stdout;
	if (!err || fileno(err) <= 0)
		err = stderr;
	if (!dbg || fileno(dbg) <= 0)
		dbg = stderr;

	pyout = PyFile_FromFile(out, "", "w", 0);
	pyerr = PyFile_FromFile(err, "", "w", 0);
	pydbg = PyFile_FromFile(dbg, "", "w", 0);

	PyObject *object = executeFunction("layman.debug", "Message",
					"(sOOO)",
					module,
					pyout,
					pyerr,
					pydbg);

	Py_DECREF(pyout);
	Py_DECREF(pyerr);
	Py_DECREF(pydbg);

	if (!object)
		return NULL;

	Message *ret = malloc(sizeof(Message));
	ret->object = object;

	return ret;
}

/**
 * Set the debug level.
 *
 * \param debug_level the debug level
 *
 * \return True on success, False on failure.
 */
int messageSetDebugLevel(Message *m, int debug_level)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_debug_level", "(I)", debug_level);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Set the debug verbosity.
 *
 * \param debug_verbosity the debug verbosity
 *
 * \return True on success, False on failure.
 */
int messageSetDebugVerbosity(Message *m, int debug_verbosity)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_debug_verbosity", "(I)", debug_verbosity);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Set the info level.
 *
 * \param info_level the info level
 *
 * \return True on success, False on failure.
 */
int messageSetInfoLevel(Message *m, int info_level)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_info_level", "(I)", info_level);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Set the warning level.
 *
 * \param warn_level the warning level
 *
 * \return True on success, False on failure.
 */
int messageSetWarnLevel(Message *m, int warn_level)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_warn_level", "(I)", warn_level);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Activates colors in the output
 *
 * \return 1 on success, 0 on failure
 */
int messageSetColorsOn(Message *m)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "color_on", NULL);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Deactivates colors in the output
 *
 * \return 1 on success, 0 on failure
 */
int messageSetColorsOff(Message *m)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "color_off", NULL);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Sets the methods to be debugged.
 *
 * \param mth the list of methods to be debugged, separated by comas
 *
 * \return 1 on success, 0 on failure
 */
int messageSetDebugMethods(Message *m, const char* mth)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_debug_methods", "(s)", mth);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Sets the classes to be debugged.
 *
 * \param mth the list of classes to be debugged, separated by comas
 *
 * \return 1 on success, 0 on failure
 */
int messageSetDebugClasses(Message *m, const char* cla)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_debug_classes", "(s)", cla);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

/**
 * Sets the variables to be debugged.
 *
 * \param mth the list of variables to be debugged, separated by comas
 *
 * \return 1 on success, 0 on failure
 */
int messageSetDebugVariables(Message *m, const char* var)
{
	if (!m || !m->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(m->object, "set_debug_variables", "(s)", var);
	int ret;

	if (obj)
		ret = 1;
	else
		ret = 0;

	Py_DECREF(obj);

	return ret;
}

void messageFree(Message *m)
{
	if (m && m->object)
	{
		Py_DECREF(m->object);
	}
	if (m)
		free(m);
}

PyObject *_messageObject(Message* m)
{
	if (m && m->object)
		return m->object;
	else
		Py_RETURN_NONE;
}
