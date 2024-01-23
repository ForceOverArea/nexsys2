from ctypes import CDLL, c_char_p, c_double, c_int, c_uint, c_void_p
from os import path

GEQSLIB_DLL = CDLL(path.join(path.dirname(__file__), "libgeqslib.so"))
"""
The precompiled library of extern "C" functions in the Rust `geqslib` crate.
"""

RUST_ERROR_OCCURRED = -1
"""
Value returned by functions when a miscellaneous error occurs
on the Rust side of an FFI function.
"""

GEQSLIB_DLL.new_context_hash_map.restype            = c_void_p

GEQSLIB_DLL.new_default_context_hash_map.restype    = c_void_p

GEQSLIB_DLL.add_const_to_ctx.argtypes               = [c_void_p, c_char_p, c_double]

GEQSLIB_DLL.solve_equation.argtypes                 = [c_char_p, c_void_p, c_double, c_double, c_double, c_double, c_uint]
GEQSLIB_DLL.solve_equation.restype                  = c_void_p

GEQSLIB_DLL.new_system_builder.argtypes             = [c_char_p, c_void_p]
GEQSLIB_DLL.new_system_builder.restype              = c_void_p

GEQSLIB_DLL.try_constrain_with.argtypes             = [c_void_p, c_char_p]
GEQSLIB_DLL.try_constrain_with.restype              = c_int
WILL_CONSTRAIN                                      = 1
WILL_NOT_CONSTRAIN                                  = 0
WILL_OVERCONSTRAIN                                  = 2

GEQSLIB_DLL.is_fully_constrained.argtypes           = [c_void_p]
GEQSLIB_DLL.is_fully_constrained.restype            = c_int
FULLY_CONSTRAINED                                   = 1
NOT_CONSTRAINED                                     = 0

GEQSLIB_DLL.build_system.argtypes                   = [c_void_p]
GEQSLIB_DLL.build_system.restype                    = c_void_p

GEQSLIB_DLL.debug_system_builder.argtypes           = [c_void_p]

GEQSLIB_DLL.specify_variable.argtypes               = [c_void_p, c_char_p, c_double, c_double, c_double]
GEQSLIB_DLL.specify_variable.restype                = c_int

GEQSLIB_DLL.solve_system.argtypes                   = [c_void_p, c_double, c_uint]
GEQSLIB_DLL.solve_system.restype                    = c_char_p

GEQSLIB_DLL.free_context_hash_map.argtypes          = [c_void_p]

GEQSLIB_DLL.free_system_builder.argtypes            = [c_void_p]

GEQSLIB_DLL.free_system.argtypes                    = [c_void_p]

GEQSLIB_DLL.free_solution_string.argtypes           = [c_char_p]






