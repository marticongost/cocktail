#-*- coding: utf-8 -*-
"""
Test suite for the Cocktail web development toolkit.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
if __name__ == "__main__":
    from unittest import main
    from cocktail.tests.modelingtests import *
    from cocktail.tests.events import *
    from cocktail.tests.schema import *
    from cocktail.tests.html import *
    main()

