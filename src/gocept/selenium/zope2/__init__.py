#############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

import Lifetime
import Testing.ZopeTestCase
import Testing.ZopeTestCase.threadutils
import Testing.ZopeTestCase.utils
import Zope2
import gocept.selenium.base


try:
    # Zope 2 >= 2.11
    import Testing.ZopeTestCase.layer
    BASE_LAYERS = (Testing.ZopeTestCase.layer.ZopeLiteLayer, )
except ImportError:
    # Zope 2 < 2.11
    BASE_LAYERS = ()


class Layer(gocept.selenium.base.Layer):

    def setUp(self):
        # adapted from Testing.ZopeTestCase.utils.startZServer() to make
        # host/port configurable
        Testing.ZopeTestCase.threadutils.setNumberOfThreads(1)
        log = None
        thread = Testing.ZopeTestCase.threadutils.QuietThread(
            target=Testing.ZopeTestCase.threadutils.zserverRunner,
            args=(self.host, self.port, log))
        thread.setDaemon(True)
        thread.start()

        # notify ZopeTestCase infrastructure that a ZServer has been started
        Testing.ZopeTestCase.utils._Z2HOST = self.host
        Testing.ZopeTestCase.utils._Z2PORT = self.port

        super(Layer, self).setUp()

    def tearDown(self):
        Lifetime.shutdown(0, fast=1)
        super(Layer, self).tearDown()


class TestCase(gocept.selenium.base.TestCase,
               Testing.ZopeTestCase.FunctionalTestCase):

    layer = Layer(*BASE_LAYERS)

    def _app(self):
        # Testing.ZopeTestCase.sandbox.Sandbox swapping of the DemoStorage is a
        # little... crude:
        #
        # ZApplicationWrapper is instantiated with a DB from
        # Testing/custom_zodb, which is never used later on, since Sandbox
        # passes in the connection (to the current DB) to use instead. This
        # connection is also stored globally in
        # Testing.ZopeTestCase.sandbox.AppZapper (and passed to requests via
        # the bobo_traverse monkey-patch there) -- which means that there only
        # ever is one single ZODB connection, among the test code and the HTTP
        # requests, and among concurrent requests. This clearly is not what we
        # want.
        #
        # Thus, this rewrite of the upstream method, that properly changes the
        # DB in ZApplicationWrapper and does *not* use AppZapper, yielding a
        # new connection upon each traversal. (For reference and since it took
        # me quite a while to figure out where everything is: this code is
        # adapted from the original Sandbox._app and the normal Zope2 startup
        # in Zope2.__init__).

        Zope2.startup()
        db, aname, version = Zope2.bobo_application._stuff
        db = Testing.ZopeTestCase.ZopeLite.sandbox()
        Zope2.bobo_application._stuff = db, aname, version
        app = Zope2.bobo_application()
        app = Testing.ZopeTestCase.utils.makerequest(app)
        Testing.ZopeTestCase.connections.register(app)
        return app
