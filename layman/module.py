from __future__ import print_function

import os

from layman.output import Message

class InvalidModuleName(Exception):
    '''An invalid or unknown module name.'''

class Module(object):
    '''
    Class to define and hold our plugin-module

    @type name: string
    @param name: The module name
    @type namepath: string
    @param namepath: The path to the new module
    @param output: The output for any information
    '''
    def __init__(self, name, namepath, output):
        self.name = name
        self._namepath = namepath
        self.kids_names = []
        self.kids = {}
        self.output = output
        self.initialized = self._initialize()


    def _initialize(self):
        '''
        Initializes the plug-in module

        @rtype bool: reflects success or failure to initialize the module
        '''
        self.valid = False
        try:
            mod_name = '.'.join([self._namepath, self.name])
            self._module = __import__(mod_name, [], [], ['not empty'])
            self.valid = True
        except ImportError as e:
            self.output.error('Module._initialize(); failed to import %(mod) '\
                'error was: %(err)' % ({'err': e, 'mod': mod_name}))
            return False
        self.module_spec = self._module.module_spec
        for submodule in self.module_spec['provides']:
            kid = self.module_spec['provides'][submodule]
            kidname = kid['name']
            kid['module_name'] = '.'.join([mod_name, self.name])
            kid['is_imported'] = False
            self.kids[kidname] = kid
            self.kids_names.append(kidname)
        return True


    def get_class(self, name):
        '''
        Retrieves a module class desired

        @type name: string
        @param name: the plug-in module's name
        @rtype mod_class: instance of plug-in module's class
        '''
        if not name or name not in self.kids_names:
            raise InvalidModuleName('Module name "%(name)" was invalid or not'\
                    'part of the module "%(mod_name)"' ({'mod_name':self.name,
                                                         'name': name}))
        kid = self.kids[name]
        if kid['is_imported']:
            module = kid['instance']
        else:
            try:
                module = __import__(kid['module_name'], [], [], ["not empty"])
                kid['instance'] = module
                kid['is_imported'] = True
            except ImportError:
                raise
        mod_class = getattr(module, kid['class'])
        return mod_class


class Modules(object):
    '''
    Dynamic module system for loading and retrieving any of the
    installed layman modules and/or provided class'

    @param path: Optional path to the "modules" directory or defaults to
                 the directory of this file + "/modules"
    @param namepath: Optional python import path to the "modules" directory or
                     defaults to the directory name of this file + ".modules"
    @param output: Optional output, defaults to layman.output.Message object
    '''
    def __init__(self, path=None, namepath=None, output=None):
        if path:
            self._module_path = path
        else:
            self._module_path = os.path.join(
                (os.path.dirname(os.path.realpath(__file__))), 'modules')
        if namepath:
            self._namepath = namepath
        else:
            self._namepath = '.'.join(os.path.dirname(
                os.path.realpath(__file__)), 'modules')
        if output:
            self.output = output
        else:
            self.output = Message()
        self._modules = self._get_all_modules()
        self.module_names = sorted(self._modules)


    def _get_all_modules(self):
        '''
        Scans the overlay modules dir for loadable modules

        @rtype dict of module_plugins
        '''
        module_dir = self._module_path
        importables = []
        names = os.listdir(module_dir)
        for entry in names:
            if entry.startswith('__'):
                continue
            try:
                os.lstat(os.path.join(module_dir, entry, '__init__.py'))
                importables.append(entry)
            except EnvironmentError:
                pass

        kids = {}
        for entry in importables:
            new_module = Module(entry, self._namepath, self.output)
            for module_name in new_module.kids:
                kid = new_module.kids[module_name]
                kid['parent'] = new_module
                kids[kid['name']] = kid
        return kids


    def get_module_names(self):
        '''
        Retrieves all available module names

        @rtype: list of installed module names available
        '''
        return self.module_names


    def get_class(self, modname):
        '''
        Retrieves a module class desired

        @type modname: string
        @param modname: the module class name
        '''
        if modname and modname in self.module_names:
            mod = self._modules[modname]['parent'].get_class(modname)
        else:
            raise InvalidModuleName('Module name "%(name)s" was invalid or'\
                ' not found.' % ({'name': modname}))
        return mod


    def get_description(self, modname):
        '''
        Retrieves the module class decription

        @type modname: string
        @param modname: the module class name
        @rtype: string of modules class decription
        '''
        if modname and modname in self.module_names:
            mod = self._modules[modname]['description']
        else:
            raise InvalidModuleName('Module name "%(name)s" was invalid or'\
                ' not found.' % ({'name': modname}))
        return mod


    def get_functions(self, modname):
        '''
        Retrieves the module class exported function names

        @type modname: string
        @param modname: the module class name
        @rtype: list of the modules class exported function names
        '''
        if modname and modname in self.module_names:
            mod = self._modules[modname]['functions']
        else:
            raise InvalidModuleName('Module name "%(name)s" was invalid or'\
                ' not found.' % ({'name': modname}))
        return mod


    def get_func_descriptions(self, modname):
        '''
        Retrieves the module class  exported functions descriptions

        @type modname: string
        @param modname: the module class name
        @rtype: dict of the modules class exported functions descriptions
        '''
        if modname and modname in self.module_names:
            desc = self._modules[modname]['func_desc']
        else:
            raise InvalidModuleName('Module name "%(name)s" was invalid or'\
                ' not found.' % ({'name': modname}))
        return desc
