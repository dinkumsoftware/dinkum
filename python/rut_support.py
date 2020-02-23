#!/usr/bin/env python3
# dinkum/python/rut_support.py
''' 
rut ==> Run Unit Tests

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

Has a class FilterTests:
    Used to manage which unittests are run, i.e
    filters away some of the tests.

Has a some functions:
    should_skip_module_for_importability_problems()
        Returns True if "import module_name" generates
        some kind of Error that requires that module_name
        NOT be searched for unittests.
        
        The Error could be:
            the module_name can't be found --or--
            there might be be a syntax error in the module itself
'''

# 2020-02-?? tc refactored from in line in exe:
#               dinkum_python_run_unittests.py
# 2020-02-23 tc should_skip_module_for_importability_problems()
#               removed exception of ignored problems in /bin dir


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

class FilterTests :
    ''' Manages a variety of filters for determining
    which unittests to run.  There are multiple filter
    types which are each specified by a string (typically
    from the command line:

    python filename     *.py
    dir_path            Has a / in it -or- "." -or- ".."
                        dir_path must be somewhere in the
                        full pathname of .py file
    Test_Case           Test_*  
    test_function       test_*
    module_name         [p0.p1.p2.]module_name

    A list of filter strings are passed in at construction time.
    '''

    # Class functions

    # These test for the type of filter
    # The testing order is important
    # See order_of_is_xxx_funcs
    def is_python_filename (spec) :
        ''' Must end in .py '''
        return spec.endswith(".py")
        
    def is_dir_path(spec) :
        ''' Must have a / in it 
        or be standalone . or ..
        '''
        return os.sep in spec   or \
               spec == "."      or \
               spec == ".."

    def is_test_case(spec) :
        ''' Must start with Test_'''
        return spec.startswith("Test_")

    def is_test_function(spec) :
        ''' Must start with test_'''
        return spec.startswith("test_")

    def is_module_name(spec) :
        ''' Anything can be a module name '''
        return spec is not None and spec != ""


    # The order to parse a string filter is important
    order_of_is_xxx_funcs=[ is_python_filename,
                            is_dir_path,
                            is_test_case,
                            is_test_function,
                            is_module_name,
                            ]

    def is_legal_filter_spec(spec) :
        ''' Returns True if spec is a
        legal filter specifier and False
        otherwise.

        '''

        # The order is in general important
        # is_xxx_order is [] of the is_* functions
        # in the order to run them
        for is_xxx in FilterTests.order_of_is_xxx_funcs :
            if is_xxx(spec) :
                return True

        # Not a filter we recognize
        return False


    def __init__(self, filter_spec_list) :
        ''' Parse and sorts filter_spec_list into
        self.filters dictionary where
            key: is name of entity, e.g python_filename
            value: is list of filter_specs of that type

        If ANY dir/filename filters exist, have_pathname_filters
        will be True.

        If ANY test_Case/function filters exist,
        have_testname_filters will be True.

        If ANY filters exist, have_filters will be True
        '''

        def strip_is_(func) :
            ''' func should be one of the is_XXX functions.
            strips "is_" from the front of func name
            and returns it as string.
            '''
            to_strip = "is_"  # what we remove from the front

            # Get the function name as a string
            ret_str = func.__name__
            if ret_str.startswith(to_strip) :
                ret_str = ret_str[len(to_strip):]
            return ret_str

        # Init filters to empty lists
        self.filters={}
        for is_xxx_func in FilterTests.order_of_is_xxx_funcs :
            # Extract the name of the function and strip of leading is_
            key = strip_is_(is_xxx_func)
            self.filters[ key ] = []

        # Go thru all the supplied filter specs
        # and put them in right list in self.filters
        if filter_spec_list :
            for filter_spec in filter_spec_list :
                for is_xxx_func in FilterTests.order_of_is_xxx_funcs :
                    # Match ?
                    if is_xxx_func(filter_spec) :
                        # Yep, stuff it in appropriate list
                        self.filters[ strip_is_(is_xxx_func) ].append( filter_spec)

                        # On to next filter spec
                        break ;

        # We have to diddle some of the filters a bit
        self._diddle_filters()

        # Figure out what kind of filters we have

        self.have_pathname_filters = False
        # Will be true if any of these filters exist
        for filter_name in [ "python_filename",
                             "dir_path",
                             "module_name" ] :
            if len(self.filters[filter_name]) > 0 :
                self.have_pathname_filters = True
                break

        # Ditto for tests base on TestCase or test_function
        self.have_testname_filters = False
        for filter_name in [ "test_case",
                             "test_function" ] :
            if len(self.filters[filter_name]) > 0 :
                self.have_testname_filters = True
                break

        # Will be true if ANY are set
        self.have_filters = self.have_pathname_filters or \
                            self.have_testname_filters




    def _diddle_filters(self) :
        ''' 
        Alters self.filters:

        python_filename:
        Has a python filename with an optional path prepended.
        If the pathname has a . or .. in it, we must expand
        to the abspathname

        dir_path:
        The filters as entered have a / in them or
        are . or ..

        We change those filters to insure:
            2. Any filter with . or .. in it is expanded to
               the full pathname.

            1. They all begin AND end with a /
               This ensures that entered pathcomponent must match in full
               a entered foo gets turned into /foo/ and which makes
               a/b/foo/c match, but NOT a/b/foobar/c
        '''

        # work function to test for . or .. in a pathname
        def has_dot_or_dotdot(pathname) :
            ''' returns True if pathname contains . or .. 
            '''

            if "."           == pathname   : return True
            if "."+os.sep    in pathname   : return True
                                           # os.sep+'dot' makes no sense
                                   
            if ".."          == pathname   : return True
            if ".." + os.sep in pathname   : return True
            if os.sep + ".." in pathname   : return True

            # No . or ..
            return False
            


        ### python_filename changes
        key="python_filename"
        filters = self.filters[key]
        new_filters = []
        # Scan all the dir_path filters.
        # diddle each one and stuff in new_filters
        for pf in filters :
            # expand path (not filename) if has /./ or /../
            if has_dot_or_dotdot(os.path.dirname(pf)) :
                # Convert to absolute path
                pf = os.path.abspath(pf)

            # Insert revised filter
            new_filters.append(pf)

        # Substitute diddled filters
        self.filters[key] = new_filters


        ### dir_path changes
        key="dir_path"
        filters = self.filters[key]
        new_filters = []
        # Scan all the dir_path filters.
        # diddle each one and stuff in new_filters
        for dp in filters :
            # expand if has /./ or /../
            if has_dot_or_dotdot(dp) :
                # Convert to absolute path
                dp = os.path.abspath(dp)

            # Surround with single /
            if not dp.startswith(os.sep) :
                dp = os.sep + dp
            if not dp.endswith(os.sep) :
                dp = dp + os.sep

            # Insert revised filter
            new_filters.append(dp)

        # Substitute diddled filters
        self.filters[key] = new_filters


    def passes_filter(self, test) :
        ''' Searches all non-empty filters using test (and it's
        derived pathname and modulename) and returns
        True if test should be run and False otherwise.

        test  A unittest.TestCase
        '''
        # Any filters to test against?
        if not self.have_filters :
            return True  # It must pass
        
        # Get location of where test came from
        (dotted_module_name, our_test_case, our_test_function) = parse_test_name(test)
        pathname = filename_from_dotted_module_name(dotted_module_name)

        # Test against each filter, returning
        # if we get a match
        if self.matches_python_filename(pathname) :
            return True

        if self.matches_dir_path(pathname) :
            return True

        if self.matches_test_case(our_test_case) :
            return True

        if self.matches_test_function(our_test_function) :
            return True

        if self.matches_module_name( dotted_module_name ) :
            return True

        # Filters exist and test matched None of them
        return False


    def matches_python_filename(self, filename) :
        ''' Returns True if there is a corresponding
        filter and argument matches it.
        '''
        filters = self.filters["python_filename"]
        if filters :
            # test must come from a file in filters []
            for filter in filters :
                if filename.endswith ( filter ) :
                    return True # We matched, test passes
        # Nothing matched --or-- no filter
        return False

    def matches_dir_path(self,pathname) :
        ''' Returns True if there is a corresponding
        filter and argument matches it.
        '''
        filters = self.filters["dir_path"]
        if filters :
            # test must come from a dir/subdir in filters []
            for dirname in filters :
                if dirname in pathname :
                    return True # We matched, test passes
        # Nothing matched --or-- no filter
        return False


    def matches_test_case(self,our_test_case) :
        ''' Returns True if there is a corresponding
        filter and argument matches it.
        '''
        filters = self.filters["test_case"]
        if filters :
            # TestCase name must match
            for test_case in filters :
                if our_test_case == test_case :
                    return True # We matched, test passes
        # Nothing matched --or-- no filter
        return False


    def matches_test_function(self, our_test_function) :
        ''' Returns True if there is corresponding filter
                    and argument matches it. '''
        filters = self.filters["test_function"]
        if filters :
            # test_function name must match
            for test_function in filters :
                if our_test_function == test_function :
                    return True # We matched, test passes
        # Nothing matched --or-- no filter
        return False

    def matches_module_name(self,dotted_module_name) :
        ''' Returns True if there is corresponding filter
        and argument matches it.
        '''
        filters = self.filters["module_name"]
        if filters :
            # test must come from a module in filters []
            for modname in filters :
                if modname in dotted_module_name :
                    return True # We matched, test passes
        # Nothing matched --or-- no filter
        return False


    def filter_TestSuite(self, input_test_suite, output_test_suite=None) :
        ''' Applies filters to all the tests in input_test_suite.
        Surviving tests are put into output_test_suite (if non-None)
        or into a newly created TestSuite.

        In either event, resulting TestSuite is returned.

        '''
        # Need to make new output_test_suite
        if not output_test_suite :
            # Yes
            output_test_suite = unittest.TestSuite()

        for test in tests_from_TestSuite(input_test_suite) :
            if self.passes_filter(test) :
                output_test_suite.addTest(test)

        return output_test_suite


    def is_filtered_by_pathname (self, pathname) :
        ''' returns TRUE is pathname should NOT be processed, i.e.
        it is filtered away.
        return False if pathanme SHOULD be processed.

        Unlike filter_TestSuite(), The filtering decision
        is based solely on pathname.  If it can't decide,
        it returns False to postpone the decision.
        '''
        # The algorithm
        # 4 cases:
        #    NO file_filters, NO test_filters return False
        #    NO file_filters,    test_filters return False
        #       file_filters,    test_filters return False
        #       file_filters, No test_filters return results of filtering

        # Detect the last case
        need_file_filtering = self.have_pathname_filters and not self.have_testname_filters
        if not need_file_filtering :
            return False

        # We have to actually filter the pathname

        # Test against each filter, returning
        # if we get a match
        if self.matches_python_filename(pathname) :
            return False

        if self.matches_dir_path(pathname) :
            return False

        dotted_module_name = dotted_module_name_from_filename(pathname)
        if self.matches_module_name( dotted_module_name ) :
            return False

        # Filters exist and pathname matched None of them
        return True



### Standalone functions
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

        # Import Error, i.e. not on PYTHONPATH
        # Warn and pass it along, it will be trapped as an error later
        efw.issue_error("Not_Findable_for_Import", module_name, pathname )

        # do Not Skip this file, the error will be reported twice
        # once by us (just now) and once when test is run

    # do Not Skip this file
    return (False, efw.need_immediate_os_return() )

    


# Test code
import unittest
from   dinkum.mas_unittest.utils import *
import itertools


class Test_rut_support(unittest.TestCase) :
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


    def test_FilterTests_is_python_filename(self) :
        self.assertTrue( FilterTests.is_python_filename("foo.py"))
        self.assertTrue( FilterTests.is_python_filename("/a/b/foo.py"))
        self.assertTrue( FilterTests.is_python_filename("c/foo.py"))        

        self.assertFalse( FilterTests.is_python_filename("foo.pyx"))
        self.assertFalse( FilterTests.is_python_filename("/a/b/foopy"))
        self.assertFalse( FilterTests.is_python_filename("c/foo.ext"))        
        self.assertFalse( FilterTests.is_python_filename(""))        
        
    def test_FilterTests_is_dir_path(self) :
        self.assertTrue( FilterTests.is_dir_path("/foo"))
        self.assertTrue( FilterTests.is_dir_path("/a/b/foo"))
        self.assertTrue( FilterTests.is_dir_path("foo/"))        

        self.assertFalse( FilterTests.is_dir_path("foo.pyx"))
        self.assertFalse( FilterTests.is_dir_path("b foopy x "))
        self.assertFalse( FilterTests.is_dir_path(""))

        self.assertTrue(  FilterTests.is_dir_path("."))
        self.assertTrue(  FilterTests.is_dir_path(".."))        

    def test_FilterTests_is_test_case(self) :
        self.assertTrue( FilterTests.is_test_case("Test_abc"))
        self.assertTrue( FilterTests.is_test_case("Test_a_b"))

        self.assertFalse( FilterTests.is_test_case("test_whatever"))
        self.assertFalse( FilterTests.is_test_case("xyzzy"))
        self.assertFalse( FilterTests.is_test_case(""))
        
    def test_FilterTests_is_test_function(self) :
        self.assertTrue( FilterTests.is_test_function("test_abc"))
        self.assertTrue( FilterTests.is_test_function("test_a_b"))

        self.assertFalse( FilterTests.is_test_function("Test_whatever"))
        self.assertFalse( FilterTests.is_test_function("xyzzy"))
        self.assertFalse( FilterTests.is_test_function(""))

    def test_FilterTests_is_module_name(self) :
        # As currently written, almost anything can be a module_name
        self.assertTrue( FilterTests.is_module_name("test_abc"))
        self.assertTrue( FilterTests.is_module_name("Test_whatever"))

        self.assertFalse( FilterTests.is_module_name(""))
        self.assertFalse( FilterTests.is_module_name(None))


    def test_FilterTests_is_legal_filter_spec(self) :
        # Basically anything is a legal spec, but we just want to make
        # sure it runs
        self.assertTrue( FilterTests.is_legal_filter_spec("a/b/c/bar.py"))        
        self.assertTrue( FilterTests.is_legal_filter_spec("x/y"))        
        self.assertTrue( FilterTests.is_legal_filter_spec("test_whatever"))        
        self.assertTrue( FilterTests.is_legal_filter_spec("Test_whatever"))        
        self.assertTrue( FilterTests.is_legal_filter_spec("a.b.c.e.f.xyzzy"))        

    def test_FilterTests_construction(self) :

        # No specs
        ft = FilterTests( [] )
        # Make sure ft.filters has all the right entries
        self.assertTrue ( "python_filename" in ft.filters )
        self.assertTrue ( "dir_path"        in ft.filters)
        self.assertTrue ( "test_case"       in ft.filters)
        self.assertTrue ( "test_function"   in ft.filters)
        self.assertTrue ( "module_name"     in ft.filters)

        # And all of the value lists are empty
        for key in ft.filters :
            self.assertEqual( ft.filters[key], [] )

        # Put one of each type of filter spec in
        ft = FilterTests ( [ "xyzzy-mod-name",
                             "a/b/c/foo.py",
                             "test_whatever",
                             "Test_even_more",
                             "a/b/c/dir-path",
                             ] )

        self.assertEqual( ft.filters["python_filename"], ["a/b/c/foo.py"     ])
        self.assertEqual( ft.filters["dir_path"],        ["/a/b/c/dir-path/" ])
        self.assertEqual( ft.filters["test_case"],       ["Test_even_more"   ])
        self.assertEqual( ft.filters["test_function"],   ["test_whatever"    ])
        self.assertEqual( ft.filters["module_name"],     ["xyzzy-mod-name"   ])
        
        # Multiple specs of same type
        ft = FilterTests( ["a.py", "b.py", "c.py", "mod_name_0", "mod_name_1"])

        for key in ft.filters :
            if key == "python_filename" :
                self.assertEqual( len(ft.filters[key]), 3 )
                for fn in ["a.py", "b.py", "c.py" ] :
                    self.assertTrue ( fn in ft.filters[key] )
            elif key == "module_name" :
                self.assertEqual( len(ft.filters[key]), 2 )
                for mod in ["mod_name_0", "mod_name_1"] :
                    self.assertTrue ( mod in ft.filters[key] )
            else:
                self.assertEqual( 0, len(ft.filters[key]))

        # Make sure we catagorize what filters are present
        ft = FilterTests([])
        self.assertFalse ( ft.have_filters )
        self.assertFalse ( ft.have_pathname_filters )
        self.assertFalse ( ft.have_testname_filters )
        
        ft = FilterTests(["foo.py"])
        self.assertTrue  ( ft.have_filters )
        self.assertTrue  ( ft.have_pathname_filters )
        self.assertFalse ( ft.have_testname_filters )

        ft = FilterTests(["dir/"])
        self.assertTrue  ( ft.have_filters )
        self.assertTrue  ( ft.have_pathname_filters )
        self.assertFalse ( ft.have_testname_filters )

        ft = FilterTests(["a.b.c"])
        self.assertTrue  ( ft.have_filters )
        self.assertTrue  ( ft.have_pathname_filters )
        self.assertFalse ( ft.have_testname_filters )

        ft = FilterTests(["Test_case"])
        self.assertTrue  ( ft.have_filters )
        self.assertFalse ( ft.have_pathname_filters )
        self.assertTrue  ( ft.have_testname_filters )

        ft = FilterTests(["Test_function"])
        self.assertTrue  ( ft.have_filters )
        self.assertFalse ( ft.have_pathname_filters )
        self.assertTrue  ( ft.have_testname_filters )
        


    def test_FilterTests_passes_filter(self) :
        # These describe this file
        our_modulename = "dinkum.python.rut_support"
        our_pathname   = filename_from_dotted_module_name(our_modulename)

        # Construct a TestSuite of all the unittests in This module
        # Note this includes a bunch of tests from modules we import
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromName(our_modulename)

        # These are the unittests from this file
        # 1   rut_support.Test_rut_support.test_FilterTests_construction
        # 2   rut_support.Test_rut_support.test_FilterTests_is_dir_path
        # 3   rut_support.Test_rut_support.test_FilterTests_is_legal_filter_spec
        # 4   rut_support.Test_rut_support.test_FilterTests_is_module_name
        # 5   rut_support.Test_rut_support.test_FilterTests_is_python_filename
        # 6   rut_support.Test_rut_support.test_FilterTests_is_test_case
        # 7   rut_support.Test_rut_support.test_FilterTests_is_test_function
        # 8   rut_support.Test_rut_support.test_FilterTests_passes_filter
        # 9   rut_support.Test_rut_support.test_need_immediate_os_return
        #10   rut_support.Test_rut_support.test_os_return_code
        #11   rut_support.Test_rut_support.test_update_from_TestResult
        #12   rut_support.Test_rut_support.test_is_filtered_by_pathname
        num_tests_in_this_file = 12
        num_tests_in_ts = ts.countTestCases()


        # We (along with other *.py files) are in the .../python dir
        # Count how many tests there are
        num_tests_in_python_dir = 0
        for test in tests_from_TestSuite(ts) :
            (dotted_module_name, test_case, ignored) = parse_test_name(test)
            if ".python." in dotted_module_name :
                num_tests_in_python_dir += 1

        # Don't filter anything
        filter = FilterTests(None)
        for test in tests_from_TestSuite(ts) :
            self.assertTrue ( filter.passes_filter(test) )

        filter = FilterTests([])
        for test in tests_from_TestSuite(ts) :
            self.assertTrue ( filter.passes_filter(test) )

        # Filter by python_filename
        filter = FilterTests( [ "rut_support.py" ] )  # Just ours
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_this_file )

        # temp change current directory to directory of this file
        prior_cwd = os.getcwd()   
        os.chdir( os.path.dirname(os.path.abspath( __file__ )))

        filter = FilterTests( [ "./rut_support.py" ] )  # Just ours
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_this_file )

        filter = FilterTests( [ "../python/rut_support.py" ] )  # Just ours
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_this_file )

        os.chdir(prior_cwd) # leave things as we found them

        filter = FilterTests( [ "a/rut_support.py" ] )  # None should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), 0 )

        filter = FilterTests( [ "foo.py" ] )  # None should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), 0 )

        # Filter by dirname
        filter = FilterTests( [ "/python/" ] )  # All tests
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_python_dir )

        filter = FilterTests( [ "/python" ] )  # Our tests should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_python_dir )

        filter = FilterTests( [ "python/" ] )  # Our tests should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_python_dir )

        filter = FilterTests( [ "/pytho" ] )  # None should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), 0 )

        # temp change current directory to directory of this file
        prior_cwd = os.getcwd()   
        os.chdir( os.path.dirname(os.path.abspath( __file__ )))

        filter = FilterTests( [ "." ] )  # Our tests should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_python_dir )

        filter = FilterTests( [ "./" ] )  # Our tests should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_python_dir )

        filter = FilterTests( [ "../python/" ] )  # Our tests should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_python_dir )

        os.chdir(prior_cwd) # leave things as we found them

        filter = FilterTests( [ "no/such/dir" ] )  # None should pass
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), 0 )

        # Filter by TestCase
        filter = FilterTests( [ "Test_rut_support" ] )  # Just ours
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), num_tests_in_this_file )

        filter = FilterTests( [ "Test_doesnt_exist" ] )  # None
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), 0 )


        # Filter by TestCase
        filter = FilterTests( [ "test_some_bogus_name" ] )  # None
        filtered_ts = filter.filter_TestSuite(ts)
        self.assertEqual( filtered_ts.countTestCases(), 0 )


    def test_is_filtered_by_pathname (self) :
        # No filters
        filter = FilterTests( [] )
        self.assertFalse( filter.is_filtered_by_pathname ("any/file/should/pass"))

        # Test filters/functions shouldn't change this
        filter = FilterTests( ["Test_whatever", "test_whatever"] )
        self.assertFalse( filter.is_filtered_by_pathname ("any/file/should/pass"))

        # A python_filename filter
        filter = FilterTests( ["foo.py"] )
        self.assertFalse( filter.is_filtered_by_pathname ("foo.py"))
        self.assertTrue ( filter.is_filtered_by_pathname ("bar.py"))

        # Now add a test Case should change that
        # All should not be filtered
        filter = FilterTests( ["foo.py", "Test_whatever"] )
        self.assertFalse( filter.is_filtered_by_pathname ("foo.py"))
        self.assertFalse( filter.is_filtered_by_pathname ("bar.py"))

        # A dir_pathname filter
        filter = FilterTests( ["/should/match"] )
        self.assertFalse( filter.is_filtered_by_pathname ("any/file/should/match/"))
        self.assertTrue ( filter.is_filtered_by_pathname ("any/file/should_not/match/"))

        # Now add a test Case should change that
        filter = FilterTests( ["/should/match", "Test_whatever"] )
        self.assertFalse( filter.is_filtered_by_pathname ("any/file/should/match/"))
        self.assertFalse( filter.is_filtered_by_pathname ("any/file/should_not/match/"))


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



