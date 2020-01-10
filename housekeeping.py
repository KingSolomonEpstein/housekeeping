# -*- coding: utf-8 -*-
"""
Created on Jan 09 4:34 PM 2020

@Author   : Luke Goodman
@File     : housekeeping.py
@Project  : pyGHB
@Company  : G&H - Boston
@IDE      : PyCharm
"""

import logging
import builtins
import functools
import numpy
from importlib import import_module
from pathlib import Path
import configparser
import sys


def oxford(itr, conj='and'):
    assert len(itr) > 1
    if len(itr) > 2:
        c = ', ' + conj + ' '
    else:
        c = ' ' + conj + ' '
    return ', '.join([str(x) for x in itr[:-1]]) + c + str(itr[-1])


def type_assert(var, typ):
    if isinstance(typ, tuple):
        types = oxford(typ, 'or')
        assert isinstance(var, typ), f"{var} is {type(var)}, not {types}"
    else:
        assert isinstance(var, typ), f"{var} is {type(var)}, not {type(typ)}"


def depend(lst):
    _temp = []
    if isinstance(lst, str):
        lst = [lst]
    if 'logging' not in lst and logging not in dir():
        lst.append('logging')
    for x in lst:
        if x not in dir():
            _temp.append(x)
            import_module(x)
    if _temp:
        logging.warning(f'The {oxford(_temp)} modules were not imported')


class SwitchedDecorator:
    # noinspection PyUnresolvedReferences
    def __init__(self, enabled_func):
        depend(['builtins', 'functools', 'logging'])
        self._enabled = False
        self._enabled_func = enabled_func

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, new_value):
        type_assert(new_value, bool)
        self._enabled = new_value

    def __call__(self, target):
        if self._enabled:
            return self._enabled_func(target)
        return target


# noinspection PyUnresolvedReferences,DuplicatedCode
def attend(f):
    # noinspection PyUnresolvedReferences
    def g(*args, **kwargs):
        ins = tuple((*args[1:], *kwargs))
        _out = ''
        if len(ins) == 1:
            ins = f"({ins[0]})"
        try:
            if args[0].__class__.__name__ in dir(builtins):
                raise AttributeError
            else:
                try:
                    _out = f"Running: <{args[0].__class__.__name__}> " \
                           f"{args[0].__name__}.{f.__name__}{ins}"
                except AttributeError:
                    _out = f"Running: <{args[0].__class__.__name__}>." \
                           f"{f.__name__}{ins}"
        except (IndexError, AttributeError):
            _out = f"Running: {f.__name__}{ins}"
        logging.debug(_out)
        r = f(*args, **kwargs)
        if r:
            logging.debug('          ' + str(r))
        return r
    functools.update_wrapper(g, f)
    return g


attendance = SwitchedDecorator(attend)

if __name__ == "__main__":
    attendance.enabled = True


def special_append(prev, new):
    if prev and new:
        _next = ','.join((prev, new))
    elif new:
        _next = new
    else:
        _next = prev
    return _next


def dynamic_append(prev, new):  # ~~dangerous~~ ~~exec~~ ~~usage~~
    if prev and new:  # *insert scary ghost noises here*
        exec(f"{prev} = ','.join(({prev}, {new}))")
    elif new:  # *also here*
        exec(f"{prev} = {new}")
    else:
        pass


def nh(obj):  # name handler - this is to make things less verbose elsewhere
    if isinstance(obj, str):
        return obj
    else:
        return obj.__name__


def ff(flt):  # float formatter - also to make things less verbose
    type_assert(flt, (float, numpy.float))
    return f"{flt:1.3f}"


def config_all(announce=False, targ=None):  # ~~dangerous~~ ~~exec~~ ~~usage~~
    depend(['configparser', 'sys'])
    if not targ:
        targ = sys.stdout
    print('sup', file=targ)
    _name = Path(exec(__file__)).with_suffix('.ini')
    print(_name, file=targ)
    _config = configparser.ConfigParser()
    _config.read(_name)
    _all = []
    for section in _config.sections():
        print('yo', file=targ)
        for key, value in _config.items(section):
            print(f'{key}: {value}', file=targ)
            assert '(' not in value, 'Do not try to inject functions here.'
            exec(f'{key} = {value}')  # *insert scary ghost noises here*
            _all.append(key)
    if announce:
        return _all
