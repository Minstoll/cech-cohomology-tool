from collections import deque, defaultdict
from itertools import combinations
import re
import numpy as np


class Nerve:
    """
    A representation of the nerve of a manifold.

    Attributes
    ----------
    degree : int
        Dimension of the highest dimensional simplex in the nerve.
    """

    def __init__(self, simplices=None) -> None:
        """
        Constructor. If simplices is not specified, initializes with empty dict.
        Expects a dict of the form {<dim: int> : {<name of simplex: str>}}, e.g.
        {0: {'0', '1'}, 1: {'0-1'}}
        """
        if simplices is not None:
            self._simplices = defaultdict(set, simplices)
        else:
            self._simplices = defaultdict(set)

    @property
    def degree(self) -> int:
        try:
            return max(self._simplices.keys())
        except ValueError:
            raise ValueError("Cannot compute degree for empty nerve!")

    def extend(self, simplex, hollow=False) -> None:
        """
        Extend the nerve by adding the specified simplex as well as subsimplices if
        they do not yet exist in the nerve.
        """
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

        if hollow:
            self.remove(simplex)

    def delete(self, simplex) -> None:
        """
        Remove the simplex as well as its boundary and any dependent subsimplices.
        Also remove any higher dimensional simplex for which this simplex forms part of
        its boundary.
        """
        if not isinstance(simplex, Simplex):
            raise TypeError(f"Deletion not supported with {type(simplex).__name__}!")
        deg = self.degree
        dim = simplex.dim
        vset = set(simplex.verts)
        if deg > dim:
            for d in range(dim + 1, deg):
                for smplx in self._simplices[d]:
                    if vset <= set(smplx.verts):
                        self.remove(smplx)

        deletions = deque([simplex])
        while deletions:
            smplx = deletions.popleft()
            n = smplx.dim
            for bdy_elt in smplx.bdy:
                if bdy_elt not in deletions:
                    deletions.append(bdy_elt)
            self._simplices[n].remove(smplx.name)

    def add(self, simplex) -> None:
        """
        Add a simplex with no additional dependencies. Must ensure any simplex forming
        its boundary already exists in the nerve. Not recommended, can lead to
        unintended consequences.
        """
        if not isinstance(simplex, Simplex):
            raise TypeError(f"Addition not supported with {type(simplex).__name__}!")
        self._simplices[simplex.dim].add(simplex.name)

    def remove(self, simplex) -> None:
        """
        Remove the specified simplex from the nerve. Does not affect its boundaries
        or any subsimplices. Can lead to unintended consequences if this simplex is
        part of a higher dimensional simplex.
        """
        if not isinstance(simplex, Simplex):
            raise TypeError(f"Removal not supported with {type(simplex).__name__}!")
        n = simplex.dim
        if simplex.name in self._simplices[n]:
            self._simplices[n].remove(simplex.name)
            if not self._simplices[n]:
                self._simplices.pop(n, None)
        else:
            raise ValueError("Simplex not found in nerve!")

    def _pformat(self, dict_data, ind=1):
        """Pretty print dict_data."""
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

    def _comp_im_ker(self, n) -> tuple[int]:
        """
        Compute the dimension of delta_n, the boundary map that differences
        restrictions of n-forms to acquire (n+1)-forms.
        """
        deg = self.degree
        if n == deg:
            return 0, len(self._simplices[deg])
        mat_rows = [self._bdy_map(Simplex(s)) for s in self._simplices[n + 1]]
        mat = np.vstack(mat_rows)
        im_dim = int(np.linalg.matrix_rank(mat))
        ker_dim = len(self._simplices[n]) - im_dim
        return im_dim, ker_dim

    def identify(self, *vs, anchor=None) -> None:
        """
        Identify different vertices of the nerve (open sets in the cover)
        by using the smallest label of the vertices (default, otherwise uses anchor)
        for all of them, updating simplices accordingly.
        """
        if not all([isinstance(v, int) for v in vs]):
            raise TypeError("Vertices should be entered as integers!")

        if anchor is not None:
            if not isinstance(anchor, int):
                raise TypeError("Vertices should be entered as integers!")
        else:
            anchor = str(min(vs))
        v_others = set(map(lambda x: str(x), vs)) - {anchor}

        for k in range(self.degree + 1):
            for s in self._simplices[k].copy():
                changed = False
                s = Simplex(s)
                s_verts = set(s.verts)
                for s_vert in s_verts:
                    if s_vert in v_others:
                        s_verts.remove(s_vert)
                        s_verts.add(anchor)
                        changed = True
                if changed:
                    s_new = Simplex("-".join(s_verts))
                    self._simplices[k].remove(s.name)
                    self._simplices[s_new.dim].add(s_new.name)

            if not self._simplices[k]:
                self._simplices.pop(k, None)

    def fill(self, dim) -> None:
        """
        If all boundaries of a dim-dimensional simplex are present, add the interior
        of the simplex to the nerve.
        """
        for comb in combinations(self._simplices[0], r=dim + 1):
            add = True
            for i, _ in enumerate(comb):
                if (
                    Simplex("-".join(comb[:i] + comb[i + 1 :])).name
                    not in self._simplices[dim - 1]
                ):
                    add = False
                    break
            if add:
                self._simplices[dim].add(Simplex("-".join(comb)).name)

    def clear(self, dim) -> None:
        """
        Remove all dim-dimensional simplices, and consequently all simplices with
        dimension greater than dim.
        """
        deg = self.degree
        if dim > deg:
            return
        for d in range(dim, deg + 1):
            self._simplices.pop(d, None)

    def cech_cohomology(self, n) -> int:
        """
        Compute k, where the n-th Cech cohomology group of the nerve
        is isomorphic to R^k.
        """
        deg = self.degree
        if deg == 0 and n >= 0:
            return len(self._simplices[0])
        match n:
            case n if n < 0:
                raise ValueError("n must be a non-negative integer!")
            case n if n > deg:
                return 0
            case _ if n == deg:
                ker_dim = len(self._simplices[deg])
                im_dim_minus, _ = self._comp_im_ker(deg - 1)
            case 0:
                im_dim_minus = 0
                _, ker_dim = self._comp_im_ker(0)
            case _:
                _, ker_dim = self._comp_im_ker(n)
                im_dim_minus, _ = self._comp_im_ker(n - 1)
        return ker_dim - im_dim_minus

    def cech_cohomology_seq(self, n=None) -> tuple[int]:
        """
        Compute the dimension of the ith Cech cohomology group, where i runs from 0 to
        n inclusive. If n is not set, take n to be the degree of the nerve.
        """
        if n is None:
            n = self.degree
        elif n < 0:
            raise ValueError("n must be a non-negative integer!")

        cech_tup = ()
        im_dim_prev = 0
        for d in range(n + 1):
            if d > self.degree:
                return 0
            im_dim, ker_dim = self._comp_im_ker(d)
            cech_tup += (ker_dim - im_dim_prev,)
            im_dim_prev = im_dim
        return cech_tup

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Nerve):
            return False
        return self._simplices == other._simplices


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
