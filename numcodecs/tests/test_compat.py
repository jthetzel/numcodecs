# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import array
import mmap


import numpy as np
import pytest


from numcodecs.compat import ensure_bytes, PY2, ensure_contiguous_ndarray


def test_ensure_bytes():
    bufs = [
        b'adsdasdas',
        bytes(20),
        np.arange(100),
        array.array('l', b'qwertyuiqwertyui')
    ]
    for buf in bufs:
        b = ensure_bytes(buf)
        assert isinstance(b, bytes)


def test_ensure_contiguous_ndarray_shares_memory():
    typed_bufs = [
        ('u', 1, b'adsdasdas'),
        ('u', 1, bytes(20)),
        ('i', 8, np.arange(100, dtype=np.int64)),
        ('f', 8, np.linspace(0, 1, 100, dtype=np.float64)),
        ('i', 4, array.array('i', b'qwertyuiqwertyui')),
        ('u', 4, array.array('I', b'qwertyuiqwertyui')),
        ('f', 4, array.array('f', b'qwertyuiqwertyui')),
        ('f', 8, array.array('d', b'qwertyuiqwertyui')),
        ('U', 4, array.array('u', u'qwertyuiqwertyui')),
        ('u', 1, mmap.mmap(-1, 10))
    ]
    for typ, siz, buf in typed_bufs:
        a = ensure_contiguous_ndarray(buf)
        assert isinstance(a, np.ndarray)
        assert typ == a.dtype.kind
        assert siz == a.dtype.itemsize
        if PY2:  # pragma: py3 no cover
            assert np.shares_memory(a, np.getbuffer(buf))
        else:  # pragma: py2 no cover
            assert np.shares_memory(a, memoryview(buf))


def test_ensure_contiguous_ndarray_invalid_inputs():

    # object array not allowed
    a = np.array([u'Xin chào thế giới'], dtype=object)
    for e in [a, memoryview(a)]:
        with pytest.raises(TypeError):
            ensure_contiguous_ndarray(e)

    # non-contiguous arrays not allowed
    with pytest.raises(ValueError):
        ensure_contiguous_ndarray(np.arange(100)[::2])


def test_ensure_contiguous_ndarray_writable():
    # check that the writeability of the underlying buffer is preserved
    for writeable in [False, True]:
        a = np.arange(100)
        a.setflags(write=writeable)
        m = ensure_contiguous_ndarray(a)
        assert m.flags.writeable == writeable
        m = ensure_contiguous_ndarray(memoryview(a))
        assert m.flags.writeable == writeable
        if PY2:  # pragma: py3 no cover
            m = ensure_contiguous_ndarray(np.getbuffer(a))
            assert m.flags.writeable == writeable
