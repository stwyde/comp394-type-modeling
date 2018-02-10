# -*- coding: utf-8 -*-

from .types import Type


class Expression(object):
    """
    AST for simple Java expressions. Note that this package deal only with compile-time types;
    this class does not actually _evaluate_ expressions.
    """

    def static_type(self):
        """
        Returns the compile-time type of this expression, i.e. the most specific type that describes
        all the possible values it could take on at runtime. Subclasses must implement this method.
        """
        raise NotImplementedError(type(self).__name__ + " must implement static_type()")

    def check_types(self):
        """
        Validates the structure of this expression, checking for any logical inconsistencies in the
        child nodes and the operation this expression applies to them.
        """
        raise NotImplementedError(type(self).__name__ + " must implement check_types()")


class Variable(Expression):
    """ An expression that reads the value of a variable, e.g. `x` in the expression `x + 5`.
    """
    def __init__(self, name, declared_type):
        self.name = name                    #: The name of the variable
        self.declared_type = declared_type  #: The declared type of the variable (Type)

    def static_type(self):
        return self.declared_type

    def check_types(self):
        return

class Literal(Expression):
    """ A literal value entered in the code, e.g. `5` in the expression `x + 5`.
    """
    def __init__(self, value, type):
        self.value = value  #: The literal value, as a string
        self.type = type    #: The type of the literal (Type)

    def static_type(self):
        return self.type

    def check_types(self):
        return

class NullLiteral(Literal):
    def __init__(self):
        super().__init__("null", Type.null)
        self.declared_type = Type.null

    def static_type(self):
        return Type.null

class MethodCall(Expression):
    """
    A Java method invocation, i.e. `foo.bar(0, 1, 2)`.
    """
    def __init__(self, receiver, method_name, *args):
        self.receiver = receiver
        self.receiver = receiver        #: The object whose method we are calling (Expression)
        self.method_name = method_name  #: The name of the method to call (String)
        self.args = args                #: The method arguments (list of Expressions)

    def static_type(self):
        classtype = self.receiver.declared_type
        method = classtype.method_named(self.method_name)
        return(method.return_type)

    def check_types(self):
        classtype = self.receiver.declared_type

        if classtype.is_subtype_of(Type.boolean) or classtype.is_subtype_of(Type.int) or classtype.is_subtype_of(Type.double):
            raise JavaTypeError("Type {0} does not have methods".format(classtype.name))

        method = classtype.method_named(self.method_name)
        argsExpected = method.argument_types #not certain what type this is.
        args = self.args #But these are definitely expressions
        typesGot = []

        for arg in args:
            typesGot.append(arg.static_type())
            arg.check_types()


        if(len(argsExpected) != len(args)):
            raise JavaTypeError("Wrong number of arguments for {3}.{0}(): expected {1}, got {2}".format(self.method_name, len(argsExpected), len(args), classtype.name))

        for i in range(len(args)):
            typeExp = argsExpected[i]
            expressionGot = args[i]
            expressionGot.check_types()
            typeGot = expressionGot.static_type()
            if (not typeGot.is_subtype_of(typeExp)) and typesGot != argsExpected:
                raise JavaTypeError("{0}.{1}() expects arguments of type {2}, but got {3}".format(classtype.name, self.method_name, names(argsExpected), names(typesGot)))
        return

class ConstructorCall(Expression):
    """
    A Java object instantiation, i.e. `new Foo(0, 1, 2)`.
    """
    def __init__(self, instantiated_type, *args):
        self.instantiated_type = instantiated_type  #: The type to instantiate (Type)
        self.args = args                            #: Constructor arguments (list of Expressions)



    def static_type(self):
        return self.instantiated_type

    def check_types(self):
        classType = self.static_type()
        if classType == Type.null:
            raise JavaTypeError("Type null is not instantiable")

        if classType.is_subtype_of(Type.boolean) or classType.is_subtype_of(Type.int) or classType.is_subtype_of(Type.double):
            raise JavaTypeError("Type {0} is not instantiable".format(classType.name))

        argsGot = self.args
        argsExp = classType.constructor.argument_types
        typesGot = []
        for arg in argsGot:
            typesGot.append(arg.static_type())
            arg.check_types()

        if(len(argsExp) != len(argsGot)):
            raise JavaTypeError("Wrong number of arguments for {0} constructor: expected {1}, got {2}".format(classType.name, len(argsExp), len(argsGot)))
        for i in range(len(argsGot)):
            typeExp = argsExp[i]
            typeGot = argsGot[i].static_type()
            #second part checks for a weird edge case where Got (Point, Size) Expected (Point, Size) TODO: figure out why
            if (not typeGot.is_subtype_of(typeExp)) and typesGot != argsExp:
                raise JavaTypeError("{0} constructor expects arguments of type {1}, but got {2}".format(classType.name, names(argsExp), names(typesGot)))
        return

class JavaTypeError(Exception):
    """ Indicates a compile-time type error in an expression.
    """
    pass


def names(named_things):
    """ Helper for formatting pretty error messages
    """
    return "(" + ", ".join([e.name for e in named_things]) + ")"
