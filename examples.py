from nerve import Nerve, Simplex

s1 = Simplex("0-1-2")
print(s1)
print(s1.dim)
print(s1.bdy)
print(s1.verts)

n1 = Nerve({0: {"0", "3", "4"}, 1: {"3-4", "0-3"}})
n1.extend(s1)
print(n1)
print(n1.degree)
