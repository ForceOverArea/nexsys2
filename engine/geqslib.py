"""
Provides several types and methods for
properly constraining a system of equations 
and solving them with the newton-raphson method.
"""

from ctypes import c_char_p, c_double, c_int, c_uint, c_void_p
from dll.geqslib_ffi import GEQSLIB_DLL
import dll.geqslib_ffi

RUST_ERROR_OCCURRED = dll.geqslib_ffi.RUST_ERROR_OCCURRED

WILL_CONSTRAIN      = dll.geqslib_ffi.WILL_CONSTRAIN
WILL_NOT_CONSTRAIN  = dll.geqslib_ffi.WILL_NOT_CONSTRAIN
WILL_OVERCONSTRAIN  = dll.geqslib_ffi.WILL_OVERCONSTRAIN

FULLY_CONSTRAINED   = dll.geqslib_ffi.FULLY_CONSTRAINED

class Context:
    """
    A Rust `HashMap` containing symbols in an equation or
    expression and their meaning. in Python, only constant 
    values can be added to the context  
    """

    def __init__(self, with_default_values: bool = True):
        """
        Initializes a new `Context` object. If `with_default_values` is 
        set to `True`, the context will contain common math functions 
        (sin, cosh, log, etc), an 'if' function, and definitions for pi and
        Euler's number.
        """
        if with_default_values:
            self.ptr = c_void_p(GEQSLIB_DLL.new_default_context_hash_map()) 
        else:
            self.ptr = c_void_p(GEQSLIB_DLL.new_context_hash_map()) 

    def __setitem__(self, symbol: str, val: float):
        """
        Adds a new constant value to the context.
        """
        c_symbol = bytes(symbol, "utf-8")
        GEQSLIB_DLL.add_const_to_ctx(self.ptr, c_symbol, c_double(val))
        
    def release(self):
        """
        Frees the `Context` object. 
        """
        GEQSLIB_DLL.free_context_hash_map(self.ptr)

def solve_equation(
    equation: str, 
    *,
    ctx: Context = None, 
    guess: float = 1.0,
    soln_min: float = float("-inf"),
    soln_max: float = float("inf"),
    margin: float = 0.0001,
    limit: int = 100
):
    """
    Solves a 1-unknown equation given as a string.
    """
    c_equation = c_char_p(bytes(equation, "utf-8"))

    if not ctx:
        ctx = Context()

    maybe_soln = c_char_p(GEQSLIB_DLL.solve_equation(
        c_equation,
        ctx.ptr,
        c_double(guess),
        c_double(soln_min),
        c_double(soln_max),
        c_double(margin),
        c_uint(limit)
    ))

    if not maybe_soln:
        return None

    return Solution(maybe_soln)

class Solution:
    """
    A solution to a system of equations.
    """

    def __init__(self, c_string: c_char_p):
        """
        Creates a new solution to a system of equations.
        
        This will almost certainly misbehave if called by
        anything other than the `System.solve_system` method.
        """
        self.ptr = c_string

        keys_vals = [x.split("=") for x in str(self).split("\n")]
        
        self.soln_dict = { x[0] : float(x[1]) for x in keys_vals }

    def __iter__(self):
        """
        Returns an iterator over the keys and values
        in the solution to the system
        """
        return iter(self.soln_dict)

    def __getitem__(self, var: str):
        """
        Returns the value of the given variable in the solution
        """
        return self.soln_dict[var]

    def __str__(self):
        """
        Returns the utf-8 string read in from Rust. 
        """
        return self.ptr.value.decode("utf-8")

    def __del__(self):
        """
        Cleans up the memory allocated to the solution string
        by Rust.

        ### TODO: 
        This is currently a memory leak. Rust destructor fn is causing invalid pointer error.
        """
        # GEQSLIB_DLL.free_solution_string(self.ptr)

def create_context_with(ctx_dict: any, include_default_values: True):
    """
    Creates a context from a `dict` or `Solution`, optionally containing the 
    default values 
    """
    ctx = Context(include_default_values)
    
    for key in ctx_dict:
        ctx[key] = ctx_dict[key]

    return ctx

class System:
    """
    A constrained system of equations that can have
    its variables' guess values or domains changed
    prior to solving. 
    """

    def __init__(self, pointer: c_void_p):
        """
        Initializes a new `System` from a C `void *`.

        This will almost certainly not behave as desired 
        if called by anything but the `SystemBuilder.build_system`
        method.
        """
        self.ptr = pointer
        self.freed = False
        self.eqns = []
    
    def specify_variable(self, 
        var: str, 
        *,
        guess: float = 1.0, 
        min: float = float("-inf"), 
        max: float = float("inf")
    ):
        """
        Specifies a guess value and domain for a specific variable
        in the system. If an error occurs while adding the data,
        a TODO is thrown. 
        """
        status = c_int(GEQSLIB_DLL.specify_variable(
            self.ptr,
            c_char_p(bytes(var, "utf-8")),
            c_double(guess),
            c_double(min),
            c_double(max),
        ))

        if status == RUST_ERROR_OCCURRED:
            raise Exception
        
    def solve_system(self, margin: float = 0.0001, limit: int = 100):
        """
        Tries to solve the system, returning a `Solution`
        on success or `None` on failure.
        """
        maybe_soln = c_char_p(GEQSLIB_DLL.solve_system(
            self.ptr, 
            c_double(margin), 
            c_uint(limit)
        ))

        self.freed = True
        if not maybe_soln:
            return None
        
        return Solution(maybe_soln)

    def __del__(self):
        """
        Frees the system if it was not used for a solution attempt.
        """
        if not self.freed:
            GEQSLIB_DLL.free_system(self.ptr)

class SystemBuilder:
    """
    An object for building a valid `System` instance,
    which represents a constrained system of equations.
    """

    def __init__(self, equation: str, ctx: Context = None):
        """
        Creates a new SystemBuilder object for building a 
        constrained system of equations 
        """
        self.freed = True # no memory malloc'ed yet

        if not ctx:
            ctx = Context()

        maybe_builder = c_void_p(GEQSLIB_DLL.new_system_builder(
            c_char_p(bytes(equation, "utf-8")), ctx.ptr
        ))
        if not maybe_builder:
            raise Exception

        self.freed = False
        self.eqns = [equation]
        self.ptr = maybe_builder

    def try_constrain_with(self, equation: str):
        """
        Tries to further constrain the system of 
        equations with the given equation, adding it
        to the system if it does.
        """
        status = c_int(GEQSLIB_DLL.try_constrain_with(
            self.ptr, c_char_p(bytes(equation, "utf-8"))
        ))
        
        if status == WILL_NOT_CONSTRAIN:
            return 0
        
        elif status == WILL_OVERCONSTRAIN:
            return 2
        
        elif status == RUST_ERROR_OCCURRED:
            raise Exception
        
        self.eqns.append(equation)
        return 1

    def is_fully_constrained(self):
        """
        Checks whether the system is fully 
        constrained, returning a boolean indicating 
        its status.
        """
        status = c_int(GEQSLIB_DLL.is_fully_constrained(self.ptr))

        if status == RUST_ERROR_OCCURRED:
            raise Exception
        
        if status.value == FULLY_CONSTRAINED:
            return True
        
        return False
    
    def build_system(self):
        """
        Tries to build a constrained system of equations,
        returning a new `System` object or `None` if a 
        constrained system cannot be built. 
        """
        if not self.is_fully_constrained():
            return None

        maybe_system = c_void_p(GEQSLIB_DLL.build_system(self.ptr))
        self.freed = True 

        if maybe_system:
            sys = System(maybe_system)
            sys.eqns = self.eqns
            return sys

        else:
            return None

    def __del__(self):
        """
        Frees the `SystemBuilder` object if it was not used to
        make a constrained system of equations.
        """
        if not self.freed:
            GEQSLIB_DLL.free_system_builder(self.ptr)