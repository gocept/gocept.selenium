#############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from gocept.selenium.wsgi.testing import SimpleApp
from gocept.selenium.wsgi.testing import SimpleApp2
import gocept.selenium.wsgi


class TestWSGITestCase(gocept.selenium.wsgi.TestCase):

    layer = gocept.selenium.wsgi.Layer(SimpleApp())

    def test_wsgi_layer(self):
        self.assertTrue(self.layer['httpd_thread'].is_alive())

    def test_simple_app(self):
        self.selenium.open('/')
        self.selenium.assertTextPresent('Hello from javascript')


class TestWSGILayerName(gocept.selenium.wsgi.TestCase):
    """ We introduce a new test layer with a different application.
    The name of the application is used in the name of the layer in order
    to have the testrunner distinguish the two layers."""

    layer = gocept.selenium.wsgi.Layer(SimpleApp2())

    def test_layer_name(self):
        self.assertEqual(self.layer.__name__, 'Layer.SimpleApp2')
