#!/usr/bin/env python3
# VagrIRC Virc library
import os

from ..base import BaseServices


class Anope2Services(BaseServices):
    """Implements support for Anope2 Services."""
    name = 'anope2'
    release = '2.0.1'
    url = 'https://github.com/anope/anope/archive/{release}.zip'
