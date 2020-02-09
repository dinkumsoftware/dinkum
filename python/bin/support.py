#!/usr/bin/env python3
# dinkum/project/bin/support.py
''' 
Has support classes and functions for executable script:
    dinkum_python_run_unittests
which is probably in the same directory we are.

Has a class EFW
  which is used for for managing "Failures, Errors, Warnings"
  (hence the name, note first letter in each word)

  Per unittest vocabulary....

    An Error is something broken in trying to run the unittest.
    This is probably some kind of import error.

    A Failure is the unittest being run did not pass, i.e
    it had some kind of self.assert..() that wasn't True.

  In addition to unittest failures and errors  We
  (the dinkum_python_run_unittests.py) can detect
  Errors and Warnings.
    Our Errors are generally import problems.
    Warnings are files that don't comply with dinkum coding
        standards.
    Errors only come from actually running the unittests


Has a some functions:
    should_skip_module_for_importability_problems()
        Returns True if "import module_name" generates
        some kind of Error that requires that module_name
        NOT be searched for unittests.
        
        The Error could be:
            the module_name can't be found --or--
            there might be be a syntax error in the module itself
'''

import sys
from   dinkum.python.modnames    import *


# What main() can return to the operating system
os_ret_val_good              = 0
os_ret_val_exception_raised  = 1
os_ret_val_cmd_line_failures = 2 # handled by argparse    
os_ret_val_errors            = 3
os_ret_val_failures          = 4
os_ret_val_warnings          = 5


class EFW :
    ''' Manages Errors, Failures, Warnings

    Keeps a count of each.  Use issue_XXX
    to increment the error/failure/warning count
    and report it to stderr.

    failfast         stop on first failure/error/warning
    ignore_warnings  
    are_listing      Not running tests, only showing tests
                     means failfast is ignored

    Use os_return_code() to determine what error code
        to return to the operating system.  See os_ret_val_XXX

    Use need_immediate_os_return() to tell if should
        immediately stop executing because ErrorFailure/Warnings
        and failfast

    '''
    def __init__(self, failfast=False, ignore_warnings=False, are_listing=False):
        ''' Set num_failures/errors/warnings to 0
        remember:
           failfast         stop on first failure/error/warning
           ignore_warnings  Completely ignore any warning
           are_listing      --listing, never exit early
        '''
        self.num_errors=0
        self.num_failures=0
        self.num_warnings=0

        self.failfast        = failfast
        self.ignore_warnings = ignore_warnings
        self.are_listing     = are_listing


    def update_from_TestResult( self, test_result ) :
        ''' Adds the errors and failures from test_result
        (a unittest.TestResult class) into our totals.
        '''

        # From https://docs.python.org/3/library/unittest.html

        # unittest.TestResult.errors
        # A list containing 2-tuples of TestCase instances and strings
        # holding formatted tracebacks. Each tuple represents a test
        # which raised an unexpected exception.

        # unittest.TestResult.failures
        # A list containing 2-tuples of TestCase instances and strings
        # holding formatted tracebacks. Each tuple represents a test
        # where a failure was explicitly signalled using the TestCase.assert*() methods.

        num_errors_in_test_result = len( test_result.errors)
        self.num_errors += num_errors_in_test_result

        num_failures_in_test_result = len( test_result.failures)
        self.num_failures += num_failures_in_test_result

    def need_immediate_os_return(self) :
        ''' returns a non-zero os return code if failfast
        and there is a Failure, Error, or non-ignored warning.

        Returns 0 error code if:
            Not failfast                               --or--
            are_listing                                --or--
            no errors/failures/warnings                --or--
            no errors/failures  and  ignoring warnings  
        '''

        # They want to stop/exit on first error?
        if  self.are_listing :
            # we never failfast if just listing and
            # not actually returning tests
            return os_ret_val_good
        elif not self.failfast :
            # nope
            return os_ret_val_good
        else:
            # failfast is True
            # Immediate return on any Failure, Error, or non-ignored Warning
            return self.os_return_code()
        
        assert False, "Impossible Place"

        

    def os_return_code(self) :
        ''' Returns the os return code that should be passed back to the operating
        system.
        '''
        if self.num_errors :
            return os_ret_val_errors

        elif self.num_failures :
            return os_ret_val_failures

        elif not self.ignore_warnings and self.num_warnings :
            return os_ret_val_warnings

        else :
            # No errors/failures/warnings
            return os_ret_val_good

        # Can't get here
        assert False, "Impossible Place"
        

    def issue_error(self, error_msg, module_name, filename, trailing_error_msg=None, file=sys.stderr) :
        ''' See _issue_workhorse()
        '''
        self.num_errors   += 1
        return self._issue_workhorse( "ERROR", error_msg, module_name, filename, trailing_error_msg, file)

    def issue_failure(self, error_msg, module_name, filename, trailing_error_msg=None, file=sys.stderr) :
        ''' See self._issue_workhorse()
        '''
        self.num_failures += 1
        return self._issue_workhorse( "FAILURE", error_msg, module_name, filename, trailing_error_msg, file)

    def issue_warning(self, warning_msg, module_name, filename, trailing_warning_msg=None, file=sys.stderr) :
        ''' See self._issue_workhorse()
        '''
        self.num_warnings += 1
        return self._issue_workhorse( "WARNING", warning_msg, module_name, filename, trailing_warning_msg, file)

    def _issue_workhorse(self, error_failure_warning_msg, main_msg, module_name, filename, trailing_msg, file) :
        ''' Sends error/failure/warning message to file of the form:

        <error_failure_warning_msg>:<main_msg> module_name:<module_name> filename:<filename>
        <trailing_error_msg>
        '''
        print ("%s:%s module_name:%s filename:%s" %(error_failure_warning_msg, main_msg, module_name, filename),
               file=file)
        if trailing_msg :
            print (trailing_msg, file=file)


    def announce_results(self, stream=None) :
        '''
        Prints number of failures/errors/warnings
        to stream (sys.stderr if None)

        It is silent if no failures/errors/warnings
        '''
        # Use Default stream?
        if not stream :
            stream = sys.stderr

        # We are silent if aren't any problems
        if self.num_errors   == 0  and \
           self.num_failures == 0  and \
           self.num_warnings == 0  :
            # No problems found, be silent
            return
        
        # Make the announcement
        # In general we try to mimic the output of unittest.run(), e.g.
        #     FAILED (failures=2, errors=2)

        print ("FAILED (failures=%d, errors=%d, warnings=%d) # prior from unittest.run(), additions from dinkum" % (self.num_failures, self.num_errors, self.num_warnings),
               file=stream)

def should_skip_module_for_importability_problems(module_name, pathname, efw) :
    ''' Examines python "module_name" whose *.py file is pathname
    for importability problems.
    efw is a class EFW which keeps track of Failures/Errors/Warnings

    Returns tuple (skip_module, immediate_exit_code)

    skip_module is true if "import module_name" generates some kind of error
    that requires that module_name NOT be searched for unittests.

    immediate_exit is non-zero if caller needs to immediately exit.
    immediate_exit should be passed back to the operating system.
    This is generally caused by Failure/Error/Warning and failfast
    when NOT listing.

    The Failure could be:
        the module_name can't be found --or--
        there might be be a syntax error in the module itself

    Both are announced to sys.stderr.  Only the later (syntax error) results
    in a True return to force the module to be skipped, otherwise it will
    will "crash" the unittest.TestLoader and this program.

    The module_name can't be found type of error is not skipped because
    it will be properly detected and reported later (all be it in a 
    confusing manner) by the normal unittest infrastructure.  Since
    we don't skip it, it will be reported twice.  hopefully our error
    message is more understandable than the the unittest error message.

    pathname should correspond to the absolute path to module_name.py
    it is only used for error printout
    '''

    # can the module be found for import?
    if is_findable_for_import(module_name) :
        # import module_name will find the file
        # 
        # Detect if any errors arise during the import of the module
        # If there are any such errors.... then the loader.loadTestsFromName()
        # will "crash".  i.e. it will print the stack trace/error from
        # the import and punt.  We don't want that.  We'll precatch any import errors ;
        # announce them as a warning ; and skip the test so loader won't crash
        #     NOTE: To test this... run with --ignore_NO_PYTHON_UNITTESTS switch
        #           and see dinkum/python/test_data/*
        import_err_msg = has_import_errors( module_name ) 
        if import_err_msg :
            # Some kind of problem importing the module
            efw.issue_error("ErrorDuringImport", module_name, pathname,
                            import_err_msg )
            # Throw this file away
            # otherwise will crash the whole program
            return (True, efw.need_immediate_os_return() )

    else :
        # The module_name CANNOT be found for import
        # This is normally an error, where if we just
        # carry on with the process the error will be
        # flagged and reported.
        # 
        # there is an exception where we want to NOT process the module
        # and suppress it's error messages:
        #     the file is in a *bin directory.
        # I.E. if it's in a bin directory it is suppose to be an executable
        # script which doesn't have unittest code and is typically not
        # importable as *bin probably doesn't have an __init__.py
        #
        #     NOTE: To test this... run with --ignore_NO_PYTHON_UNITTESTS switch
        #           and see dinkum/python/test_data/*

        # In a *bin directory?
        if os.path.dirname(pathname).endswith("bin") :
            # yes, skip the file
            return (True, efw.need_immediate_os_return() )

        # Import Error, i.e. not on PYTHONPATH
        # Warn and pass it along, it will be trapped as an error later
        efw.issue_error("Not_Findable_for_Import", module_name, pathname )

        # do Not Skip this file, the error will be reported twice
        # once by us (just now) and once when test is run

    # do Not Skip this file
    return (False, efw.need_immediate_os_return() )

    


# Test code
import unittest
import itertools

class Test_support(unittest.TestCase) :
    def test_os_return_code(self) :
        # Enforce assumptions
        self.assertEqual(0, os_ret_val_good)

        efw = EFW(False, False, False)

        # No errors/failures/warnings
        self.assertEqual(efw.os_return_code(), os_ret_val_good)

        # Test from lowest to highest priority
        # e.g an error is reported if both errors and warnings

        # Warnings
        efw.num_warnings = 3
        self.assertEqual(efw.os_return_code(), os_ret_val_warnings)
        
        # Failures
        efw.num_failures = 1
        self.assertEqual(efw.os_return_code(), os_ret_val_failures)

        # Errors
        efw.num_errors = 4
        self.assertEqual(efw.os_return_code(), os_ret_val_errors)


        # Repeat the tests using issue_XXX() instead of directly
        # incrementing efw.num_XXX
        efw = EFW(False, False, False)

        # Suppress issue_XXX() output normally sent to std.stderr
        with open(os.devnull, "w") as devnull :

            # Test from lowest to highest priority
            # e.g an error is reported if both errors and warnings

            # Warnings
            efw.issue_warning("", "", "", "", file=devnull)
            self.assertEqual(efw.os_return_code(), os_ret_val_warnings)
        
            # Failures
            efw.issue_failure("", "", "", "", file=devnull)
            self.assertEqual(efw.os_return_code(), os_ret_val_failures)

            # Errors
            efw.issue_error("", "", "", "", file=devnull)        
            self.assertEqual(efw.os_return_code(), os_ret_val_errors)



    def test_need_immediate_os_return(self) :

        # For generating all combinations of args for EFW()
        all_bools = [True, False]


        # No failures/errors/warnings, shouldn't say return no matter what
        for (failfast, no_warnings, listing) in itertools.product( all_bools, all_bools, all_bools) :
            efw = EFW(failfast, no_warnings, listing)
            self.assertEqual( efw.need_immediate_os_return(), os_ret_val_good )

        
        # are listing, shouldn't say return no matter what
        for (failfast, no_warnings) in itertools.product( all_bools, all_bools) :
            efw = EFW(failfast, no_warnings, are_listing=True)
            efw.num_errors=1
            efw.num_failures=1
            efw.num_warnings=1                        
            self.assertEqual( efw.need_immediate_os_return(), os_ret_val_good )
        

        # aren't failing fast. shouldn't say return no matter what
        for (no_warnings, are_listing) in itertools.product( all_bools, all_bools) :
            failfast = False
            efw = EFW(failfast, no_warnings, are_listing)
            efw.num_errors=1
            efw.num_failures=1
            efw.num_warnings=1                        
            self.assertEqual( efw.need_immediate_os_return(), os_ret_val_good )


        # Simulate failures/errors/warnings

        # Warnings Only
        efw= EFW(failfast=True, ignore_warnings=False, are_listing=False)
        efw.num_warnings   = 1
        self.assertEqual( efw.need_immediate_os_return(), os_ret_val_warnings )
        
        efw= EFW(failfast=True, ignore_warnings=True, are_listing=False)
        efw.num_warnings   = 1
        self.assertEqual( efw.need_immediate_os_return(), os_ret_val_good )

        efw= EFW(failfast=True, ignore_warnings=True, are_listing=False)
        efw.num_warnings   = 1
        efw.num_failures   = 1
        self.assertEqual( efw.need_immediate_os_return(), os_ret_val_failures )

        efw.num_errors     = 1
        self.assertEqual( efw.need_immediate_os_return(), os_ret_val_errors )


    def test_update_from_TestResult(self) :
        efw_cnts = (1,2,3)
        efw = EFW()
        (efw.num_errors, efw.num_failures, efw.num_warnings) = efw_cnts

        tr_cnts = (4, 5 )
        tr = unittest.TestResult()
        tr.errors   = [(None, None)] * tr_cnts[0]    # Dummy errors
        tr.failures = [(None, None)] * tr_cnts[1]    # Dummy failures

        efw.update_from_TestResult(tr)

        self.assertEqual( efw.num_errors  , efw_cnts[0] + tr_cnts[0] )
        self.assertEqual( efw.num_failures, efw_cnts[1] + tr_cnts[1] )
        self.assertEqual( efw.num_warnings, efw_cnts[2]              )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



