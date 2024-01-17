''' cheatsheet_methods_static_and_class.py

How to use @classmethod and @staticmethod

Both @classmethod and @staticmethod are attached to a Class
(NOT an instance)

@classmethods CAN alter class variables in the defining class.
cls is the Class provided as the first argument to a class method.
(Just like self for a class instance)

@staticmethods CANNOT alter class variable in the defining class

'''

# Definition
class Foo:
    class_variable = 4 ;

    @staticmethod
    def smeth(call_src) :
        print ("staticmethod: smeth()", call_src )

    @classmethod
    def cmeth(cls, call_src) :
        print ("classmethod: cmeth()", call_src )

        Foo.class_variable += 1
        cls.class_variable += 1

    def inst_method_calling_static(self) :
        Foo.smeth( "From inst_method_calling_static, Foo.smeth()" )
        self.smeth("From inst_methodcalling_class,   self.smeth()")

        # Foo.class_variable  += 1

    def inst_method_calling_class(self) :
        Foo.cmeth( "From inst_method_calling_class(), Foo.cmeth()" )
        self.cmeth("From inst_method_calling_class(), self.cmeth()")

        Foo.class_variable  += 1
        self.class_variable += 1
        

# Usage, i.e. how to call

# Calling staticmethod
Foo.smeth  ("external call from class"   )
Foo().smeth("external call from instance")
Foo().inst_method_calling_static()       

# Produces
#  staticmethod: smeth() external call from class
#  staticmethod: smeth() external call from instance
#  staticmethod: smeth() From inst_method_calling_static, Foo.smeth()
#  staticmethod: smeth() From inst_methodcalling_class,   self.smeth()

print()

# Calling classmethod
Foo.cmeth  ("external call from class"   )
Foo().cmeth("external call from instance")
Foo().inst_method_calling_class()       

# Produces
#  classmethod: cmeth() external call from class
#  classmethod: cmeth() external call from instance
#  classmethod: cmeth() From inst_method_calling_class(), Foo.cmeth()
#  classmethod: cmeth() From inst_method_calling_class(), self.cmeth()

print()

# Be careful about inadvertentely SETTING class variables from an instance.
# You make create an instance variable of the same name
# https://stackoverflow.com/questions/44460724/can-i-access-class-variables-using-self

class Bar:
    cls_var = 1 ;

    # "Bar.cls_var"         works anywhere

    # "type(self).cls_var"  works anywhere

    # "self.cls_var"        works for READ access
    #                       creates an instance variable cls_var for writes

