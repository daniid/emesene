'''
This provides extensions functionality.
You should use both if you want to provide or to use them.

Extensions in your code
=======================
    Basic
    -----
        If you want to use extensions, you'll have to "initialize" a category first::
        
            import extensions
            extensions.category_register("category name")
        

        This should be done only once. Anyway, doing this more than once is not an error.::
        
            extensions.get_extensions("category name") #if you want a LIST of extensions
            extensions.get_default("category name") #if you want ONE extension
        
    Advanced
    --------
        Sometimes you want to be SURE that the extensions behave "the right way".
        To do this, you can provide an interface: an interface is just
        a class that has all the method we require; example::
        
            Class IFoo:
                def __init__(self, some, args):
                    raise NotImplementedError
                def method_foo(self, we, like, args):
                    raise NotImplementedError
                def method_bar(self, some, other, args):
                    raise NotImplementedError
        
        When you create the category with category_register, you can specify
        it using C{extensions.category_register("category name", IFoo)}

Providing extensions
====================
    Extensions can be provided through plugins, and they are a powerful way
    of enhancing emesene. They are just classes with a predefined API, 
    "connected" to a category.
    This is done through extensions.register("category name", extension_class)
    When developing an extension, always check if it has a required interface:
    if so, implement it all, or your extension will be rejected!
    Thanks to L{plugin_lint} (TODO) you should be able to check if your
    extension is well-formed.
    You should also put a class attribute (tuple) called "implements" in your
    extension: each of its elements will be a reference to an interface you're
    implementing
'''


class Category:
    '''This completely handles a category'''
    def __init__(self, name, interface):
        '''Constructor: creates a new category
    @param name: The name of the new category.
    @param interface: The interface every extension is required to match. 
        If it's None, no interface is required
        '''
        self.name = name
        self.interface = interface
        self.classes = {}
        self.instances = {}
    
    def register(self, cls):
        '''This will "add" a class to the possible extension.
    @param cls: A Class, NOT an instance
    @raise ValueError: if cls doesn't agree to the interface
        '''
        if self.interface is not None:
            if not is_implementation(cls, self.interface):
                raise ValueError, \
                        "cls doesn't agree to the interface: %s" % \
                         (str(self.interface))
        class_name = _get_class_name(cls)
        self.classes[class_name] = cls

    def get_extensions(self):
        '''return a list of ready-to-use extension instances'''
        return [self._instance_of(class_name) 
            for class_name in self.classes.keys()]

    def _instance_of(self, class_name):
        '''Given a class name, will return a ready-to-use instance. 
        Every "trick" (hey, only if necessary), will be done here.
        '''
        if class_name in self.instances:
            return self.instances[class_name]

        instance = self.classes[class_name]()
        self.instances[class_name] = instance
        return instance

    def get_default(self):
        '''return ONE extension instance. It will be chosen with preferences'''
        #put here your choosing logic (preferences)
        available = self.get_extensions()
        if available:
            return available[0] #that's just a test: we should choose better
        return None


_categories = {} #'CategoryName': Category('ClassName')

def category_register(category, interface=None):
    '''Add a category'''
    _categories[category] = Category(category, interface)

def register(category_name, cls):
    '''Register cls as an Extension for category. 
    If the class doesn't agree to the required interface, raises ValueError.
    If the category doesn't exist, it creates it(but returns False).
    It doesn't instanciate that class immediately.
    @return: False if the category didn't exist. Probably you made a mistake, True otherwise.
    '''
    get_category(category_name).register(cls)

def get_category(category_name):
    '''Get a Category object'''
    return _categories[category_name]

def get_extensions(category_name):
    '''return a list of ready-to-use extension instances'''
    return get_category(category_name).get_extensions()

def get_default(category_name):
    '''This will return a "default" extension, chosen through Config (TODO)'''
    return get_category(category_name).get_default()

def is_implementation(cls, interface_cls):
    '''Check if cls implements all the methods provided by interface_cls.
    Note: every cls implements None.
    '''
    for method in [attribute for attribute in dir(interface_cls)
            if not attribute.startswith('_')]:
        if not hasattr(cls, method):
            return False
    return True

def _get_class_name(cls):
    '''Returns the full name of a class: module.class
    For instances, call get_full_name(self.__class__)'''
    return '.'.join([cls.__module__, cls.__name__])

