from ctypes import CDLL, c_double, c_uint, c_void_p
from os import path

GMATLIB_DLL = CDLL(path.join(path.dirname(__file__), "libgmatlib.so"))
"""
The precompiled library of extern "C" functions in the Rust `gmatlib` crate.
"""

GMATLIB_DLL.new_double_matrix.argtypes          = [c_uint, c_uint]
GMATLIB_DLL.new_double_matrix.restype           = c_void_p

GMATLIB_DLL.new_double_identity_matrix.argtypes = [c_uint]
GMATLIB_DLL.new_double_identity_matrix.restype  = c_void_p

GMATLIB_DLL.inplace_row_swap.argtypes           = [c_void_p, c_uint, c_uint]
GMATLIB_DLL.inplace_row_swap.restype            = c_uint

GMATLIB_DLL.inplace_scale.argtypes              = [c_void_p, c_double]
GMATLIB_DLL.inplace_scale.restype               = c_uint

GMATLIB_DLL.inplace_row_scale.argtypes          = [c_void_p, c_uint, c_double]
GMATLIB_DLL.inplace_row_scale.restype           = c_uint

GMATLIB_DLL.inplace_row_add.argtypes            = [c_void_p, c_uint, c_uint]
GMATLIB_DLL.inplace_row_add.restype             = c_uint

GMATLIB_DLL.inplace_scaled_row_add.argtypes     = [c_void_p, c_uint, c_uint, c_double]
GMATLIB_DLL.inplace_scaled_row_add.restype      = c_uint

GMATLIB_DLL.multiply_matrix.argtypes            = [c_void_p, c_void_p]
GMATLIB_DLL.multiply_matrix.restype             = c_void_p

GMATLIB_DLL.augment_with.argtypes               = [c_void_p, c_void_p]
GMATLIB_DLL.augment_with.restype                = c_void_p

GMATLIB_DLL.subset.argtypes                     = [c_void_p, c_uint, c_uint, c_uint, c_uint]
GMATLIB_DLL.subset.restype                      = c_void_p

GMATLIB_DLL.trace.argtypes                      = [c_void_p]
GMATLIB_DLL.trace.restype                       = c_double

GMATLIB_DLL.transpose.argtypes                  = [c_void_p]
GMATLIB_DLL.transpose.restype                   = c_void_p

GMATLIB_DLL.try_inplace_invert.argtypes         = [c_void_p]
GMATLIB_DLL.try_inplace_invert.restype          = c_uint

GMATLIB_DLL.index_double_matrix.argtypes        = [c_void_p, c_uint, c_uint]
GMATLIB_DLL.index_double_matrix.restype         = c_double

GMATLIB_DLL.index_mut_double_matrix.argtypes    = [c_void_p, c_uint, c_uint, c_double]
GMATLIB_DLL.index_mut_double_matrix.restype     = c_uint

GMATLIB_DLL.clone_double_matrix.argtypes        = [c_void_p]
GMATLIB_DLL.clone_double_matrix.restype         = c_void_p

GMATLIB_DLL.free_double_matrix.argtypes         = [c_void_p] 
