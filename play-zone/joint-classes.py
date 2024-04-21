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
    c1 = 1

    def __init__(self, x):
        self.x = x


class C2(object):
    c2 = 2

    def __init__(self, y, k):
        self.y = y
        self.k = k


class C3(object):
    c3 = 3

    def __init__(self, z):
        self.z = z


class C0(C1, C2, C3):
    '''
    **Class C0(C1, C2, C3)**
    A class that represents C0 and inherits from C1, C2, and C3.

    **Methods:**
    - `__init__(self, k='k', x='x', y='y', z='z')`: Initializes an instance of C0 with optional parameters k, x, y, and z. Calls the `__init__` methods of C1, C2, and C3 using the `super()` function.
    - `print(self)`: Prints the attributes of the instance of C0.

    '''

    def __init__(self, k='k', x='x', y='y', z='z'):
        # Super for C2
        super(C1, self).__init__(y, k)
        # Super for C3
        super(C2, self).__init__(z)
        # Super for C1
        super(C0, self).__init__(x)

    def print(self):
        for e in [e for e in dir(self) if not e.startswith('__')]:
            print(f'{e}=\t {self.__getattribute__(e)}')


# %% ---- 2024-04-18 ------------------------
# Play ground
if __name__ == '__main__':
    c0 = C0()
    c0.print()

    print('---- __mro__ ----')
    for i, e in enumerate(C0.__mro__):
        print(i, e)


# %% ---- 2024-04-18 ------------------------
# Pending


# %% ---- 2024-04-18 ------------------------
# Pending
