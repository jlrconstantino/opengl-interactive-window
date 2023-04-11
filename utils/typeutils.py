# Dependências
from inspect import signature
from functools import wraps


# Descritor de um atributo
class Descriptor:
    def __init__(self, name=None, **opts):
        self.name = name
        for key, value in opts.items():
            setattr(self, key, value)
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


# Descritor para garantir tipagem
class Typed(Descriptor):
    expected_type = type(None)
    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                "expected '{}' to be {}".format(
                    self.name, 
                    str(self.expected_type).replace('<', '{').replace('>', '}')
                )
            )
        super().__set__(instance, value)


# Descritor para garantir valores sem sinal
class Unsigned(Descriptor):
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("expected an unsigned value")
        super().__set__(instance, value)


# Inteiro
class Integer(Typed):
    expected_type = int


# Inteiro sem sinal
class UnsignedInteger(Integer, Unsigned):
    pass


# String
class String(Typed):
    expected_type = str


# Decorador para asserções de tipo por meio de atributos
def typeassert(*ty_args, _is_method=False, **ty_kwargs):

    # Decorador interno
    def decorator(func):

        # Desabilita a verificação em modo otimizado
        if not __debug__:
            return func
        
        # Mapeamento dos nomes aos tipos
        func_sig = signature(func)
        bound_types = func_sig.bind_partial(*ty_args, **ty_kwargs).arguments

        # Envólucro da função
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Imposição de tipos aos argumentos
            bound_values = func_sig.bind(*args, **kwargs)
            iterable = iter(bound_values.arguments.items())
            if _is_method == True:
                next(iterable)
            for name, value in iterable:
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError(
                            "argument {} must be {}".format(
                                name, 
                                str(bound_types[name]).replace('<', '{').replace('>', '}')
                            )
                        )
            
            # Finalização
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Levanta uma exceção caso a variável não seja do tipo especificado
def check_type(var, nam, typ):
    if not isinstance(var, typ):
        raise TypeError (
            "expected '{}' to be {}".format(
                nam, str(typ).replace('<', '{').replace('>', '}')
            )
        )


# Levanta uma exceção caso a variável, possivelmente nula, não seja do tipo especificado
def check_nullable_type(var, nam, typ):
    if var is not None:
        return check_type(var, nam, typ)