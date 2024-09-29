from collections import deque, defaultdict
import re
import numpy as np


class Nerve:
    """
    A representation of the nerve of a manifold.

    Attributes
    ----------
    degree : int
        Dimension of the highest dimensional simplex in the nerve.

    Methods
    -------
    __init__(simplices):
        Constructor. If simplices is not specified, initializes with empty dict.
        Expects a dict of the form {<dim: int> : {<name of simplex: str>}}, e.g.
        {0: {'0', '1'}, 1: {'0-1'}}
    extend(simplex):
        Extend the nerve by adding the specified simplex as well as subsimplices if
        they do not yet exist in the nerve.
    _pformat(dict_data):
        Pretty print dict_data.
    """

    def __init__(self, simplices=None) -> None:
        if simplices is not None:
            self._simplices = defaultdict(set, simplices)
        else:
            self._simplices = defaultdict(set)

    @property
    def degree(self) -> int:
        return max(self._simplices.keys())

    def extend(self, simplex) -> None:
        if not isinstance(simplex, Simplex):
            raise TypeError(f"Extension not supported with {type(simplex).__name__}!")
        additions = deque([simplex])

        while additions:
            smplx = additions.popleft()
            n = smplx.dim
            for bdy_elt in smplx.bdy:
                if bdy_elt not in additions:
                    additions.append(bdy_elt)
            self._simplices[n].add(smplx.name)

    def _pformat(self, dict_data, ind=1):
        ret_str = ""
        for k, v in dict_data.items():
            ret_str += (
                "\t" * ind
                + f"{str(k)}: \n"
                + "\t" * (ind + 1)
                + f"{', '.join([item for item in v])}\n"
            )
        ret_str = "{\n" + ret_str + "}"
        return ret_str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._pformat(self._simplices)})"

    def _bdy_map(self, smplx) -> np.ndarray:
        """
        Return a list of -1, 1, 0 corresponding to the signs of the n-forms
        on the n-simplices in an ordered list, when the boundary map is applied
        to give a form on smplx of dimension n + 1.
        """
        n_plus = smplx.dim
        ordered_nplx = sorted([Simplex(name) for name in self._simplices[n_plus - 1]])
        ret = np.zeros((1, len(ordered_nplx)))
        for i, bdy_elt in enumerate(smplx.bdy):
            ret[0, ordered_nplx.index(bdy_elt)] = (-1) ** i
        return ret

    def _comp_im_ker(self, n):
        """
        Compute the dimension of delta_n, the boundary map that differences
        restrictions of n-forms to acquire (n+1)-forms.
        """
        mat_rows = [self._bdy_map(s) for s in self._simplices[n + 1]]
        mat = np.vstack(mat_rows)
        im_dim = int(np.linalg.matrix_rank(mat))
        ker_dim = len(self._simplices[n]) - im_dim
        return im_dim, ker_dim

    def cech_cohomology(self, n) -> int:
        """
        Compute k, where the n-th Cech cohomology group of the nerve
        is isomorphic to R^k.
        """
        if self.degree == 0 and n >= 0:
            return len(self._simplices[0])
        match n:
            case n if n < 0:
                raise ValueError("n must be a non-negative integer!")
            case n if n > self.degree:
                return 0
            case self.degree:
                ker_dim = len(self._simplices[self.degree])
                im_dim_minus, _ = self._comp_im_ker(self.degree - 1)
            case 0:
                im_dim_minus = 0
                _, ker_dim = self._comp_im_ker(0)
            case _:
                _, ker_dim = self._comp_im_ker(n)
                im_dim_minus, _ = self._comp_im_ker(n - 1)
        return ker_dim - im_dim_minus


class Simplex:
    """
    A representation of an n-simplex.

    Attributes
    ----------
    dim : int
        Dimension of the simplex.
    bdy : set
        Set of simplicies which constitute the boundary of the simplex.
        Avoids recursively creating many redundant objects at init by using @property
        decorator.
    verts : list of str
        List of vertices of the simplex, sorted ascending.
    name: str
        A string of ordered, dash separated integers which label the vertices of the
        simplex.
        If the simplex is a point, this is one integer cast as a string.

    Methods
    -------
    __init__(name):
        Constructor. Set attributes according to the formatted name (see above).
    """

    def __init__(self, name) -> None:
        if not re.match(r"^\d+(-\d+)*$", name):
            raise ValueError("Name must be dash separated integer form! E.g. 0-3-11-8")
        verts = name.split("-")
        self.verts = [str(v) for v in sorted([int(v) for v in verts])]
        self.dim = len(self.verts) - 1
        self.name = "-".join(self.verts)

    @property
    def bdy(self) -> list:
        bdy_lst = []
        if self.dim == 0:
            return bdy_lst
        else:
            for i in range(self.dim + 1):
                bdy_name = "-".join(self.verts[:i] + self.verts[i + 1 :])
                bdy_lst.append(Simplex(bdy_name))
            return bdy_lst

    def __lt__(self, other) -> bool:
        if not isinstance(other, Simplex):
            raise TypeError(f"Comparison not supported with {type(other).__name__}!")
        if self.dim != other.dim:
            raise ValueError("Cannot compare simplices of different dimensions!")

        for v1, v2 in zip(self.verts, other.verts):
            if int(v1) < int(v2):
                return True
            elif int(v1) > int(v2):
                return False
            else:
                continue
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Simplex):
            return False
        return self.name == other.name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"
