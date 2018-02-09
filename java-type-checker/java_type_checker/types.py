# -*- coding: utf-8 -*-


class Type(object):
    """ Represents any Java type, including both class types and primitives.
    """
    def __init__(self, name, direct_supertypes=[]):
        self.name = name
        self.direct_supertypes = direct_supertypes
        self.is_instantiable = False

    def is_subtype_of(self, other):
        """ True if this type can be used where the other type is expected.
        """
        #Catch for self not in supertypes, modifies a copy of the direct_supertypes in case user didn't spec self in list
        allSupers = [self]
        prevSize = -1
        currentSize = 1
        while currentSize > prevSize:
            prevSize = currentSize
            for super in allSupers:
                potentialNewSupers = super.direct_supertypes
                for potentialSuper in potentialNewSupers:
                    if potentialSuper not in allSupers:
                        allSupers.append(potentialSuper)
                        currentSize+=1
        #Is this messy? yes it is. I'd rather use a set in this case but apparently returning arrays and then extending sets isn't viable
        return(other in allSupers)

    def is_supertype_of(self, other):
        """ Convenience counterpart to is_subtype_of().
        """
        return other.is_subtype_of(self)


class Constructor(object):
    """ The declaration of a Java constructor.
    """
    def __init__(self, argument_types=[]):
        self.argument_types = argument_types


class Method(object):
    """ The declaration of a Java method.
    """
    def __init__(self, name, argument_types=[], return_type=None):
        self.name = name
        self.argument_types = argument_types
        self.return_type = return_type


class ClassOrInterface(Type):
    """
    Describes the API of a class-like Java type (class or interface).

    (This type model does not draw a distinction between classes and interfaces,
    and assumes they are all instantiable. Other than instantiability, the
    distinction makes no difference to us here: we are only checking types, not
    compiling or executing code, so none of the methods have implementations.)
    """
    def __init__(self, name, direct_supertypes=[], constructor=Constructor([]), methods=[]):
        super().__init__(name, direct_supertypes)
        self.name = name
        self.constructor = constructor
        self.methods = {method.name: method for method in methods}
        self.is_instantiable = True

    def method_named(self, name):
        """ Returns the Method with the given name, which may come from a supertype.
        """
        try:
            return self.methods[name]
        except KeyError:
            for supertype in self.direct_supertypes:
                try:
                    return supertype.method_named(name)
                except NoSuchMethod:
                    pass
            raise NoSuchMethod("{0} has no method named {1}".format(self.name, name))


class NullType(ClassOrInterface):
    """ The type of the value `null` in Java.
    """
    def __init__(self):
        super().__init__("null")
        self.is_instantiable = False
        self.methods = {}

    def method_named(self, name):
        raise NoSuchMethod("{0} has no method named {1}".format(self.name, name))

    def is_subtype_of(self, other):
        return True

    def is_supertype_of(self, other):
        return False





class NoSuchMethod(Exception):
    pass


# Our simple language’s built-in types

Type.void    = Type("void")

Type.boolean = Type("boolean")
Type.int     = Type("int")
Type.double  = Type("double")

Type.null    = NullType()

Type.object = ClassOrInterface("Object",
    methods=[
        Method("equals", argument_types=[object], return_type=Type.boolean),
        Method("hashCode", return_type=Type.int),
    ])
