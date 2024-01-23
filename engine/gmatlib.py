"""
Provides a `Matrix` type that supports a 
number of basic matrix-math operations. 
"""

from ctypes import c_double, c_uint, c_void_p 
from dll.gmatlib_ffi import GMATLIB_DLL

class MatrixCreationError(Exception):
    def __str__(self) -> str:
        return "cannot create a Matrix with a negative number of rows or columns"

class MatrixAugmentError(Exception):
    def __init__(self, rows_right, rows_left) -> None:
        super().__init__()

        self.rows_right = rows_right
        self.rows_left  = rows_left

    def __str__(self) -> str:
        return f"cannot augment {self.rows_left}-row Matrix with {self.rows_right}-row Matrix"

class MatrixIndexOutOfBoundsError(Exception):
    def __str__(self) -> str:
        return "index was out of bounds of Matrix"

class MatrixScalePanic(Exception):
    def __str__(self) -> str:
        return "the rust-side matrix scale method panicked"

class Matrix:
    """
    A compact Rust-based MxN matrix.
    """

    def __new__(cls, *_):
        """
        Allows loading the Rust DLL lazily.         
        """
        if not hasattr(cls, "dll"):
            cls.DLL = GMATLIB_DLL

        return super(Matrix, cls).__new__(cls)


    def __init__(self, *args):
        """
        Constructor method for `Matrix`.         
        """
        self.malloced = False

        argc = len(args)
        types = [type(i) for i in args]

        # Build matrix from list[list[float]]
        if argc == 1 and types == [list]:
            vals      = args[0]
            self.rows = len(vals) 
            self.cols = len(vals[0])

            for i in range(1, self.rows):
                if len(vals[i]) != self.cols:
                    raise MatrixCreationError
            
            self.ptr = c_void_p(Matrix.DLL.new_double_matrix(c_uint(self.rows), c_uint(self.cols))) 
            self.malloced = True

            for i in range(self.rows):
                for j in range(self.cols):
                    self[i, j] = vals[i][j]

        # Build 0 matrix with m rows and n cols 
        elif argc == 2 and types == [int, int]:
            self.rows, self.cols = args
            self.ptr = c_void_p(Matrix.DLL.new_double_matrix(c_uint(self.rows), c_uint(self.cols))) 
            self.malloced = True

        # Build from pre-existing pointer
        elif argc == 3 and types == [int, int, c_void_p]:
            self.rows, self.cols, self.ptr = args

        else:
            raise MatrixCreationError
            

    def __getitem__(self, indices: tuple) -> float:
        """
        Index operator for `Matrix` objects.
        """
        types = [type(i) for i in indices]
        argc  = len(types)

        # Indexing functionality
        if argc == 2 and types == [int, int]:
            i, j = indices
            
            if i < self.rows or j < self.cols:
                return Matrix.DLL.index_double_matrix(self.ptr, c_uint(i), c_uint(j))    

        # Slicing functionality
        elif argc == 3 and types == [int, slice, int]:
            i1, slc, j2 = indices
            j1, i2 = slc.start, slc.stop
            
            if i1 >= i2 or j1 >= j2:
                raise IndexError
            
            else:
                subset = Matrix(
                    i2 - i1 + 1,
                    j2 - j1 + 1,
                    c_void_p(Matrix.DLL.subset(self.ptr, c_uint(i1), c_uint(j1), c_uint(i2), c_uint(j2)))
                )
                subset.malloced = True
                return subset
            
        else:
            raise IndexError


    def __setitem__(self, indices: tuple, value: float) -> c_uint:
        """
        Mutable index operator for `Matrix` objects.
        """
        i, j = indices

        if i >= self.rows or j >= self.cols:
            raise MatrixIndexOutOfBoundsError

        return Matrix.DLL.index_mut_double_matrix(self.ptr, c_uint(indices[0]), c_uint(indices[1]), c_double(value))


    def __mul__(self, other):
        """
        Matrix product operator
        """

        # Matrix product
        if type(other) == Matrix:
            res  = c_void_p(Matrix.DLL.multiply_matrix(self.ptr, other.ptr))
            rows = self.rows
            cols = other.cols

        # Scale matrix
        elif type(other) in [int, float]:
            new  = self.clone()
            new.scale(other)
            rows = self.rows
            cols = self.cols
            res  = new.ptr 

        return Matrix(rows, cols, res)


    def __or__(self, other):
        """
        Matrix augmentation operator.

        Produces a new `Matrix` object by appending the columns of the 
        right operand to those of the left.
        """

        if self.rows != other.rows:
            raise MatrixAugmentError(self.rows, other.rows)
        
        rows = self.rows
        cols = self.cols + other.cols

        augment = Matrix(
            rows, 
            cols, 
            c_void_p(Matrix.DLL.augment_with(self.ptr, other.ptr))
        )
        augment.malloced = True
        return augment


    def __pow__(self, other):
        """
        Either raises the matrix to the power specified OR 
        provides shorthand representations for transpose
        or inverse operations if the right-hand operand is
        'T' or '-1', respectively.
        """
        if type(other) == str:
            if other == "-1":
                    inv = self.clone()
                    inv.invert()
                    return inv
            
            if other == "T":
                return self.transpose()

        elif type(other) in [int, float]:
            pass # TODO: make exponentiation happen


    def __str__(self) -> str:
        """
        Creates a string representation of this `Matrix` instance.
        """
        output = "["

        r = self.rows - 1
        c = self.cols - 1

        for i in range(r):
            for j in range(c):
                output += str(self[i, j]) + ", "
            output += str(self[i, c]) + "; "

        for j in range(c):
            output += str(self[r, j]) + ", "
        output += str(self[r, c]) + "]"

        return output          


    def __del__(self):
        """
        Destructor method for `Matrix` 
        """
        # Prevent double free if refrencing another `Matrix`'s ptr:
        if self.malloced:
            Matrix.DLL.free_double_matrix(self.ptr)


    def scale(self, scalar):
        """
        Scales the matrix in-place, multiplying all
        of its elements by `scalar`.
        """
        if not Matrix.DLL.inplace_scale(self.ptr, c_double(scalar)):
            raise MatrixScalePanic


    def transpose(self):
        """
        Transposes the matrix, mirroring it about its diagonal.
        """
        success = c_void_p(Matrix.DLL.transpose(self.ptr))
        
        if success != 0:
            return Matrix(self.cols, self.rows, success)

        return None


    def invert(self) -> bool:
        """
        Attempts to invert the Matrix in-place, returning a `bool`
        indicating whether the operation was successful.
        """
        return bool(Matrix.DLL.try_inplace_invert(self.ptr))


    def clone(self):
        """
        Creates a copy of the `Matrix` object.
        """
        cln = Matrix(
            self.rows,
            self.cols,
            c_void_p(Matrix.DLL.clone_double_matrix(self.ptr))
        )
        cln.malloced = True
        return cln
