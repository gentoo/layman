# -*- coding: utf-8 -*-
#################################################################################
# LAYMAN - DEBUGGING FUNCTIONS
#################################################################################
# debug.py -- Utility function for debugging
# Copyright 2005 - 2008 Gunnar Wrobel
# Distributed under the terms of the GNU General Public License v2

__version__ = "$Id: debug.py 153 2006-06-05 06:03:16Z wrobel $"

#################################################################################
##
## Dependancies
##
#################################################################################

import sys, inspect, types

from   optparse      import OptionGroup

from   layman.constants  import (codes, DEBUG_LEVEL, DEBUG_VERBOSITY,
    INFO_LEVEL, WARN_LEVEL, OFF)

from output import Message


class DebugMessage(Message):
    """fully Debug enabled subclass of output.py's Message
    """
    #FIXME: Think about some simple doctests before you modify this class the
    #       next time.

    def __init__(self, module = '',
                 out = sys.stdout,
                 err = sys.stderr,
                 dbg = sys.stderr,
                 debug_level = DEBUG_LEVEL,
                 debug_verbosity = DEBUG_VERBOSITY,
                 info_level = INFO_LEVEL,
                 warn_level = WARN_LEVEL,
                 col = True,
                 mth = None,
                 obj = None,
                 var = None):

        if mth == None: mth = ['*']
        if obj == None: obj = ['*']
        if var == None: var = ['*']

        Message.__init__(self)

        # A description of the module that is being debugged
        self.debug_env = module

        # Where should the debugging output go? This can also be a file
        self.debug_out = dbg

        # Where should the error output go? This can also be a file
        #self.error_out = err

        # Where should the normal output go? This can also be a file
        #self.std_out = out

        # The higher the level the more information you will get
        #self.warn_lev = warn_level

        # The higher the level the more information you will get
        #self.info_lev = info_level

        # The highest level of debugging messages acceptable for output
        # The higher the level the more output you will get
        #self.debug_lev = debugging_level

        # The debugging output can range from very verbose (3) to
        # very compressed (1)
        self.debug_vrb = debug_verbosity

        # Which methods should actually be debugged?
        # Use '*' to indicate 'All methods'
        self.debug_mth = mth

        # Which objects should actually be debugged?
        # Use '*' to indicate 'All objects'
        self.debug_obj = obj

        # Which variables should actually be debugged?
        # Use '*' to indicate 'All variables'
        self.debug_var = var

        # Exclude class variables by default
        self.show_class_variables = False

        # Should the output be colored?
        #self.use_color = col

        #self.has_error = False


    ############################################################################
    # Add command line options

    def cli_opts(self, parser):

        #print "Parsing debug opts"

        group = OptionGroup(parser,
                            '<Debugging options>',
                            'Control the debugging features of '
                            + self.debug_env)

        group.add_option('--debug',
                         action = 'store_true',
                         help = 'Activates debugging features.')

        group.add_option('--debug-level',
                         action = 'store',
                         type = 'int',
                         help = 'A value between 0 and 10. 0 means no debugging '
                         'messages will be selected, 10 selects all debugging me'
                         'ssages. Default is "4".')

        group.add_option('--debug-verbose',
                         action = 'store',
                         type = 'int',
                         help = 'A value between 1 and 3. Lower values yield les'
                         's verbose debugging output. Default is "2".')

        group.add_option('--debug-methods',
                         action = 'store',
                         help = 'Limits the methods that will return debugging o'
                         'utput. The function name is sufficient and there is no'
                         'difference between class methods or general functions.'
                         ' Several methods can be specified by seperating them w'
                         ' with a comma. Default is "*" which specifies all meth'
                         'ods.')

        group.add_option('--debug-classes',
                         action = 'store',
                         help = 'Limits the classes that will return debugging o'
                         'utput. Specify only the class name not including the m'
                         'odules in which the class is defined (e.g. MyModule.ma'
                         'in.Main should only be represented by "Main"). Several'
                         'classes can be specified by seperating them with a com'
                         'ma. Default is "*" which specifies all classes.')

        group.add_option('--debug-variables',
                         action = 'store',
                         help = 'Limits the variables that will return debugging'
                         ' output. Several variables can be specified by seperat'
                         'ing them with a comma. Default is "*" which specifies '
                         'all variables.')

        group.add_option('--debug-class-vars',
                         action = 'store_true',
                         help = 'In default mode the debugging code will only re'
                         'turn information on the local variable which does not '
                         'include the class variables. Use this switch to add al'
                         'l values that are provided by "self".')

        group.add_option('--debug-nocolor',
                         action = 'store_true',
                         help = 'Deactivates colors in the debugging output.')

        parser.add_option_group(group)


    #############################################################################
    # Handle command line options

    def cli_handle(self, options):

        if (options.__dict__.has_key('debug')
            and options.__dict__['debug']):
            self.set_debug_level(DEBUG_LEVEL)
        else:
            self.set_debug_level(OFF)
            return

        if (options.__dict__.has_key('debug_class_vars')
            and options.__dict__['debug_class_vars']):
            self.class_variables_on()
        else:
            self.class_variables_off()

        if (options.__dict__.has_key('debug_nocolor')
            and options.__dict__['debug_nocolor']):
            self.set_colorize(False)
        else:
            self.set_colorize(True)

        if (options.__dict__.has_key('debug_level') and
            options.__dict__['debug_level']):
            dbglvl = int(options.__dict__['debug_level'])
            if dbglvl < 0:
                dbglvl = 0
            if dbglvl > 10:
                dbglvl = 10
            self.set_debug_level(dbglvl)

        if (options.__dict__.has_key('debug_verbose') and
            options.__dict__['debug_verbose']):
            dbgvrb = int(options.__dict__['debug_verbose'])
            if dbgvrb < 1:
                dbgvrb = 1
            if dbgvrb > 3:
                dbgvrb = 3
            self.set_debug_verbosity(dbgvrb)

        for i in [('debug_methods',   self.set_debug_methods),
                  ('debug_classes',   self.set_debug_classes),
                  ('debug_variables', self.set_debug_variables),]:

            if (options.__dict__.has_key(i[0]) and
                options.__dict__[i[0]]):
                i[1](options.__dict__[i[0]])


    #############################################################################
    ## Helper Functions

    def set_module(self, module):

        self.debug_env = module

    def set_debug_methods(self, methods):

        methods = methods.split(',')

        if methods:
            self.debug_mth = methods

    def set_debug_classes(self, classes):

        classes = classes.split(',')

        if classes:
            self.debug_obj = classes

    def set_debug_variables(self, variables):

        variables = variables.split(',')

        if variables:
            self.debug_var = variables


    def set_debug_verbosity(self, debugging_verbosity = DEBUG_VERBOSITY):
        self.debug_vrb = debugging_verbosity


    def class_variables_off(self):
        self.show_class_variables = False

    def class_variables_on(self):
        self.show_class_variables = True

    #############################################################################
    ## Output Functions

    def debug (self, message, level = DEBUG_LEVEL):
        '''
        This is a generic debugging method.
        '''
        ## Check the debug level first. This is the most inexpensive check.
        if level > self.debug_lev:
            return

        ## Maybe this should be debugged. So get the stack first.
        stack = inspect.stack()

        ## This can probably never happen but does not harm to check
        ## that there is actually something calling this function
        if len(stack) < 2:
            return

        ## Get the stack length to determine indentation of the debugging output
        stacklength = len(stack)
        ls = '  ' * stacklength

        ## Get the information about the caller
        caller = stack[1]

        ## The function name of the calling frame is the fourth item in the list
        callermethod = caller[3]

        ## Is this actually one of the methods that should be debugged?
        if not '*' in self.debug_mth and not callermethod in self.debug_mth:
            return

        ## Still looks like this should be debugged. So retrieve the dictionary
        ## of local variables from the caller
        callerlocals = inspect.getargvalues(caller[0])[3]

        ## Is the caller an obejct? If so he provides 'self'
        if 'self' in callerlocals.keys():
            callerobject = callerlocals['self']
            del callerlocals['self']
            if self.show_class_variables:
                cv = inspect.getmembers(callerobject,
                                        lambda x: not inspect.ismethod(x))
                callerlocals.sync(cv)
        else:
            callerobject = None

        # Remove variables not requested
        if not '*' in self.debug_var:
            callerlocals = dict([i for i in callerlocals.items()
                                 if i[0] in self.debug_var])

        ## Is the object among the list of objects to debug?
        if (not '*' in self.debug_obj and
            not str(callerobject.__class__.__name__) in self.debug_obj):
            return

        if type(message) not in types.StringTypes:
            message = str(message)

        def breaklines(x):
            '''
            Helper function to keep width of the debugging output.

            This may look ugly for arrays but it is acceptable and not
            breaking the line would break the output format
            '''
            ## Get the number of lines we need (rounded down)
            lines = len(x) // 60
            if lines > 0:
                for j in range(lines):
                    ## Print line with continuation marker
                    print >> self.debug_out, ls + '// ' + x[0:60] + ' \\'
                    ## Remove printed characters from output
                    x = x[60:]
            ## Print final line
            print >> self.debug_out, ls + '// ' + x

        if self.debug_vrb == 1:
            # Top line indicates class and method
            c = ''
            if callerobject:
                c += 'Class: ' + str(callerobject.__class__.__name__) + ' | '
            if callermethod:
                c += 'Method: ' + str(callermethod)
            print >> self.debug_out, '// ' + c
            # Selected variables follow
            if callerlocals:
                for i,j in callerlocals.items():
                    print >> self.debug_out, '// '                              \
                          + self.maybe_color('turquoise', str(i)) + ':' + str(j)
            # Finally the message
            print >> self.debug_out, self.maybe_color('yellow', message)
            return

        if self.debug_vrb == 3:
            print >> self.debug_out, ls + '/////////////////////////////////' + \
                  '////////////////////////////////'

            # General information about what is being debugged
            #(module name or similar)
            print >> self.debug_out, ls + '// ' + self.debug_env
        print >> self.debug_out, ls + '//-----------------------------------' + \
              '----------------------------'

        ## If the caller is a class print the name here
        if callerobject:
            print >> self.debug_out, ls +                                       \
                  '// Object Class: ' + str(callerobject.__class__.__name__)

        ## If the method has been extracted print it here
        if callermethod:
            print >> self.debug_out, ls + '// '                                 \
                  + self.maybe_color('green', 'Method: ') + str(callermethod)
            if self.debug_vrb == 3:
                print >> self.debug_out, ls + '//---------------------------' + \
                      '------------------------------------'

        ## Print the information on all available local variables
        if callerlocals:
            if self.debug_vrb == 3:
                print >> self.debug_out, ls + '//'
                print >> self.debug_out, ls + '// VALUES '
            for i,j in callerlocals.items():
                print >> self.debug_out, ls + '// ------------------> '         \
                      + self.maybe_color('turquoise', str(i)) + ':'
                breaklines(str(j))
            if self.debug_vrb == 3:
                print >> self.debug_out, ls + '//------------------------------'\
                      '---------------------------------'

        # Finally print the message
        breaklines(self.maybe_color('yellow', message))

        if self.debug_vrb == 3:
            print >> self.debug_out, ls + '//-------------------------------' + \
                  '--------------------------------'
            print >> self.debug_out, ls + '/////////////////////////////////' + \
                  '////////////////////////////////'

## gloabal message handler
OUT = Message('layman')
