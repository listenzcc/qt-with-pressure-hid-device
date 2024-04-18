"""
File: joint-classes.py
Author: Chuncheng Zhang
Date: 2024-04-18
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-04-18 ------------------------
# Requirements and constants


# %% ---- 2024-04-18 ------------------------
# Function and class

class C1(object):
    """docstring for C1."""
    c1 = 1

    def __init__(self, x):
        self.x = x


class C2(object):
    """docstring for C2."""
    c2 = 2

    def __init__(self, y, k):
        self.y = y
        self.k = k


class C3(object):
    """docstring for C3."""
    c3 = 3

    def __init__(self, z):
        self.z = z


class C0(C1, C2, C3):
    def __init__(self, k='k', x='x', y='y', z='z'):
        super(C1, self).__init__(y, k)
        super(C2, self).__init__(z)
        super(C0, self).__init__(x)

    def print(self):
        for e in [e for e in dir(self) if not e.startswith('__')]:
            print(f'{e}=\t {self.__getattribute__(e)}')


# %% ---- 2024-04-18 ------------------------
# Play ground
if __name__ == '__main__':
    c0 = C0()
    c0.print()


# %% ---- 2024-04-18 ------------------------
# Pending


# %% ---- 2024-04-18 ------------------------
# Pending
