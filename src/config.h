#ifndef CONFIG_H
#define CONFIG_H

#include <Python.h>

typedef struct Config Config;

Config *createConfig(const char *argv[], int argc);

PyObject *_object(Config*);

#endif
