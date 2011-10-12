#include <Python.h>
// temp workaround for my environment
// since at times it fails to find Python.h
#include <python2.6/Python.h>
#include <stdio.h>


#include "message.h"
#include "internal.h"
#include "basic.h"


/** \defgroup message Message
 * \brief Debug message management
 *
 * This class relays all debug messages to the given files and set different
 * debug levels.
 */


PyObject *messageCreate (PythonSessionStruct *_pysession,
		FILE *out, FILE *err, 
		int infolevel, int warnlevel, 
		int col);
int SetDebugLevel (int debug_level);
int SetInfoLevel (int info_level);
int SetWarnLevel (int warn_level);
int SetColorsOn ();
int SetColorsOff ();




/** \addtogroup message
 * @{
 */

	 /** \internal */

/**
 * Message structure that is used in all functions
 */
struct MessageStruct
{

	/**
	* placeholders
	 */
	PyObject * message;
	PythonSessionStruct *pysession;
	
	/**
	* Functions
	*/
	int (* SetDebugLevel) (int debug_level);
	int (* SetInfoLevel) (int info_level);
	int (* SetWarnLevel) (int warn_level);
	int (* SetColorsOn) ();
	int (* SetColorsOff) ();
	
	
};

/**
 * Creates a Message instance with default values.
 * To modify those values, use the corresponding functions.
 *
 * \param _pysession. pointer to our running PythonSessionStruct
 * \param out where to write info
 * \param err where to write errors
 * \param dbg where to write debug information
 *
 * \return a new instance of a Message object. It must be freed with messageFree()
 */
PyObject *
messageCreate(PythonSessionStruct *_pysession,
		FILE *out, FILE *err, 
		int infolevel, int warnlevel, 
		int col)
{
	// record the pysession pointer to the structure
	pysession = _pysession;

	PyObject *pyout, *pyerr;

	if (!out || fileno(out) <= 0)
		out = stdout;
	if (!err || fileno(err) <= 0)
		err = stderr;

	pyout = PyFile_FromFile(out, "", "w", 0);
	pyerr = PyFile_FromFile(err, "", "w", 0);

	PyObject *object = pysession.executeFunction(
		"layman.output",
		"Message",
		"(sOOO)",
		pyout,
		pyerr,
		PyInt_FromLong(infolevel),
		PyInt_FromLong(warnlevel),
		PyBool_FromLong(col)
		);

	Py_DECREF(pyout);
	Py_DECREF(pyerr);

	if (!object)
		return NULL;

	return object;
}


/**
 * Set the debug level.
 *
 * \param debug_level the debug level
 *
 * \return True on success, False on failure.
 */
int 
SetDebugLevel(int debug_level)
{
	if (!message)
		return False;

	PyObject *obj = pysession.PyObject_CallMethod(
		message, "set_debug_level", "(I)", debug_level);
	int ret;

	if (obj)
		ret = True;
	else
		ret = False;

	Py_XDECREF(obj);

	return ret;
}


/**
 * Set the info level.
 *
 * \param info_level the info level
 *
 * \return True on success, False on failure.
 */
int 
SetInfoLevel(int info_level)
{
	if (!message)
		return False;

	PyObject *obj = pysession.PyObject_CallMethod(
		message, "set_info_level", "(I)",
		PyInt_FromLong(info_level));
	int ret;

	if (obj)
		ret = True;
	else
		ret = False;

	Py_XDECREF(obj);

	return ret;
}

/**
 * Set the warning level.
 *
 * \param warn_level the warning level
 *
 * \return True on success, False on failure.
 */
int 
SetWarnLevel(int warn_level)
{
	if (!message)
		return False;

	PyObject *obj = pysession.PyObject_CallMethod(
		message, "set_warn_level", "(I)",
		PyInt_FromLong(warn_level));
	int ret;

	if (obj)
		ret = True;
	else
		ret = False;

	Py_XDECREF(obj);

	return ret;
}

/**
 * Activates colors in the output
 *
 * \return 1 on success, 0 on failure
 */
int 
SetColorsOn()
{
	if (!message)
		return False;

	PyObject *obj = pysession.PyObject_CallMethod(
		message, "set_colorize", Py_True);
	int ret;

	if (obj)
		ret = True;
	else
		ret = False;

	Py_XDECREF(obj);

	return ret;
}

/**
 * Deactivates colors in the output
 *
 * \return 1 on success, 0 on failure
 */
int 
SetColorsOff()
{
	if (!message)
		return False;

	PyObject *obj = pysession.PyObject_CallMethod(
		message, "set_colorize", Py_False);
	int ret;

	if (obj)
		ret = True;
	else
		ret = False;

	Py_XDECREF(obj);

	return ret;
}


/**
 * Frees a message structure.
 */
void 
messageFree(MessageStruct *m)
{
	if (m && m->interpreter)
	{
		Py_XDECREF(m->interpreter);
	}
	if (m)
	{
		free(m);
		m = NULL;
	}
}


/** @} */
