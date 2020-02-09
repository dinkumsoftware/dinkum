# README.txt
# dinkum/python/test_data/

Describes what this directory is all about

2020-02-06 tc Initial

The contents of this directory are python files that
generate some kind of unittest error when running:
    ../bin/dinkum_python_run_unittests.py

They are prevented from being run normally (and
flagged as an error) by the existence of a file named:
    NO_PYTHON_UNITTESTS
To process these files (and see the errors):
    run dinkum_python_run_unittests.py with --ignore_NO_PYTHON_UNITTESTS switch
                                             -ign                         

The files and their associated error(s):
    test_data/not_a_package/module.py       Does not exist: not_a_package/__init__.py file
    test_data/import_syntax_error.py        Fails import, has syntax error
    test_data/module_with_test_failures.py  5 tests:test_1...test_4, two of them (2,4) fail
