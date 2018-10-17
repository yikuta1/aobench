#!/usr/bin/python
# -*- coding: utf-8 -*-


def test_1():
    import ao

    ao.ao('ao.ppm') == 0, 'error'
