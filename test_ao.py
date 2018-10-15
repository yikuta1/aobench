#!/usr/bin/python
# -*- coding: utf-8 -*-

def test_1():
    import ao
    print(ao)
    ao.ao('ao.ppm')

def test_2():
    a = 1
    b = 2
    assert a != b
