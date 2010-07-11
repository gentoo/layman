#include <Python.h>
#include "message.h"
#include "interpreter.h"

struct Message
{
	PyObject *object;
};

/*
 * TODO: This constructor is too big.
 * 	 Create a little constructor that uses default values
 * 	 and add helper functions to set the values
 */
Message *messageCreate(const char* module,
			FILE* out,
			FILE* err,
			FILE* dbg,
			int debug_level,
			int debug_verbosity,
			int info_level,
			int warn_level,
			int col,
			StringList* mth,
			StringList* obj,
			StringList* var)
{
	PyObject *pyout, *pyerr, *pydbg, *pymth, *pyobj, *pyvar;

	pyout = PyFile_FromFile(((!out || fileno(out) <= 0) ? stdout : out),
				"", "w", 0);
	pyerr = PyFile_FromFile(((!err || fileno(err) <= 0) <= 0 ? stderr : err),
				"", "w", 0);
	pydbg = PyFile_FromFile(((!dbg || fileno(dbg) <= 0) ? stderr : dbg),
				"", "w", 0);

	pymth = cListToPyList(mth);
	pyobj = cListToPyList(obj);
	pyvar = cListToPyList(var);

	PyObject *object = executeFunction("layman.debug", "Message",
					"(sOOOIIIIIOOO)",
					module,
					pyout,
					pyerr,
					pydbg,
					debug_level,
					debug_verbosity,
					info_level,
					warn_level,
					col,
					pymth,
					pyobj,
					pyvar);

	Py_DECREF(pyout);
	Py_DECREF(pyerr);
	Py_DECREF(pydbg);
	Py_DECREF(pymth);
	Py_DECREF(pyobj);
	Py_DECREF(pyvar);

	if (!object)
		return NULL;

	Message *ret = malloc(sizeof(Message));
	ret->object = object;

	return ret;
}

PyObject *_messageObject(Message* m)
{
	if (m && m->object)
		return m->object;
	else
		Py_RETURN_NONE;
}
