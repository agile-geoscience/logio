#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
# Paul Ross: cpipdev@googlemail.com
"""Provides a fairly basictwo dimensional coordinate sytem.
"""


__author__  = 'Paul Ross'
__date__    = '2009-09-25'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

#import logging
#import sys
import collections

from TotalDepth.LIS import ExceptionTotalDepthLIS

class ExceptionCoord(ExceptionTotalDepthLIS):
    """Exception class for representing Coordinates."""
    pass

class ExceptionCoordUnitConvert(ExceptionCoord):
    """Exception raised when converting units."""
    pass

#: Base units for dimensions
BASE_UNITS = 'px'

#: Map of {unit name : conversion factor to base units, ...}
UNIT_MAP = {
    None        : 1.0,  # Implied base units i.e. default
    'px'        : 1.0,
    'pt'        : 1.0,  # Actual base units i.e. BASE_UNITS
    'pc'        : 12.0,
    'in'        : 72.0,
    'cm'        : 72.0/2.54,
    'mm'        : 72.0/25.4,
}

def units():
    """Returns the unsorted list of acceptable units."""
    return UNIT_MAP.keys()

def convert(val, unitFrom, unitTo):
    """Convert a value from one set of units to another."""
    if unitFrom == unitTo:
        return val
    try:
        return val * UNIT_MAP[unitFrom] / UNIT_MAP[unitTo]
    except KeyError:
        if unitFrom not in UNIT_MAP:
            raise ExceptionCoordUnitConvert('Unsupported units %s' % unitTo)
        raise ExceptionCoordUnitConvert('Unsupported units %s' % unitFrom)

class Dim(collections.namedtuple('Dim', 'value units',)):
    """Represents a dimension as an engineering value i.e. a number and units.""" 
    __slots__ = ()

    def scale(self, factor):
        """Returns a new Dim() multiplied by a factor, units are unchanged."""
        return self._replace(value=self.value*factor)

    def divide(self, factor):
        """Returns a new Dim() divided by a factor, units are unchanged."""
        return self._replace(value=self.value/factor)

    def convert(self, u):
        """Returns a new Dim() with units changed and value converted."""
        return self._replace(value=convert(self.value, self.units, u), units=u)

    def __str__(self):
        #return 'Dim: %s (%s)' % (self.value, self.units)
        return 'Dim(%s%s)' % (self.value, self.units)

    def __add__(self, other):
        """Overload self+other, returned result has the sum of self and other.
        The units chosen are self's unless self's units are None in which case other's
        units are used (if not None)."""
        if self.units is None and other.units is not None:
            myVal = other.value + convert(self.value, self.units, other.units)
            return Dim(myVal, other.units)
        else:
            myVal = self.value + convert(other.value, other.units, self.units)
            return Dim(myVal, self.units)

    def __sub__(self, other):
        """Overload self-other, returned result has the difference of self and
        other. The units chosen are self's unless self's units are None in
        which case other's units are used (if not None)."""
        if self.units is None and other.units is not None:
            myVal = convert(self.value, self.units, other.units) - other.value
            return Dim(myVal, other.units)
        else:
            myVal = self.value - convert(other.value, other.units, self.units)
            return Dim(myVal, self.units)

    def __iadd__(self, other):
        """Addition in place, value of other is converted to my units and added."""
        # Use __add__()
        self = self + other
        return self

    def __isub__(self, other):
        """Subtraction in place, value of other is subtracted."""
        # Use __sub__()
        self = self - other
        return self

    def __lt__(self, other):
        """Returns true if self value < other value after unit conversion."""
        return (self.value < convert(other.value, other.units, self.units))

    def __le__(self, other):
        """Returns true if self value <= other value after unit conversion."""
        return (self.value <= convert(other.value, other.units, self.units))

    def __eq__(self, other):
        """Returns true if self value == other value after unit conversion."""
        return (self.value == convert(other.value, other.units, self.units))

    def __ne__(self, other):
        """Returns true if self value != other value after unit conversion."""
        return (self.value != convert(other.value, other.units, self.units))

    def __gt__(self, other):
        """Returns true if self value > other value after unit conversion."""
        return (self.value > convert(other.value, other.units, self.units))

    def __ge__(self, other):
        """Returns true if self value >= other value after unit conversion."""
        return (self.value >= convert(other.value, other.units, self.units))

def dimIn(v):
    """Returns a Dim object with the value in inches."""
    return Dim(v, 'in')

# All of these take a Dim() for each member
#
# This describes the size of a box, its members are Dim() objects
#Box         = collections.namedtuple('Box', 'width depth',)
# Padding around another object that forms the Bounding Box
# All 4 attributes are Dim() objects
#Pad         = collections.namedtuple('Pad', 'prev next parent child',)

class Box(collections.namedtuple('Box', 'width depth',)):
    """A named tuple that describes a box with width and depth as Dim() objects."""
    __slots__ = ()
    def __str__(self):
        """Stringifying."""
        return 'Box(width=%s, depth=%s)' % (self.width, self.depth)    

class Pad(collections.namedtuple('Pad', 'prev next parent child',)):
    """Padding around another object that forms the Bounding Box.
    All 4 attributes are Dim() objects"""
    __slots__ = ()
    def __str__(self):
        """Stringifying."""
        return 'Pad(prev=%s, next=%s, parent=%s, child=%s)' \
            % (self.prev, self.next, self.parent, self.child)

class Margin(collections.namedtuple('Margin', 'left right top bottom',)):
    """Margin padding around another object. All 4 attributes are Coord.Dim()
    objects."""
    __slots__ = ()
    def __str__(self):
        """Stringifying."""
        return 'Margin(left=%s, right=%s, top=%s, bottom=%s)' \
            % (self.left, self.right, self.top, self.bottom)

class Pt(collections.namedtuple('Pt', 'x y',)):
    """A point, an absolute x/y position on the plot area.
    Members are Coord.Dim()."""
    __slots__ = ()
    def __eq__(self, other):
        """Comparison."""
        return self.x == other.x and self.y == other.y

    def __str__(self):
        """Stringifying."""
        return 'Pt(x=%s, y=%s)' \
            % (self.x, self.y)
        #return 'Pt(x=%s %s, y=%s %s)' \
        #    % (self.x.value, self.x.units, self.y.value, self.y.units)

    def convert(self, u):
        """Returns a new Pt() with units changed and value converted."""
        return self._replace(x=self.x.convert(u), y=self.y.convert(u))

    def scale(self, factor):
        """Returns a new Pt() scaled by a factor, units are unchanged."""
        return self._replace(x=self.x.scale(factor), y=self.y.scale(factor))

###############################################
# Section: Helper functions for object creation
###############################################
def baseUnitsDim(theLen):
    """Returns a Coord.Dim() of length and units BASE_UNITS."""
    return Dim(theLen, BASE_UNITS)

def zeroBaseUnitsDim():
    """Returns a Coord.Dim() of zero length and units BASE_UNITS."""
    return baseUnitsDim(0.0)

def zeroBaseUnitsBox():
    """Returns a Coord.Box() of zero dimensions and units BASE_UNITS."""
    return Box(
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
        )

def zeroBaseUnitsPad():
    """Returns a Coord.Pad() of zero dimensions and units BASE_UNITS."""
    return Pad(
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
        )

def zeroBaseUnitsPt():
    """Returns a Coord.Dim() of zero length and units BASE_UNITS."""
    return Pt(zeroBaseUnitsDim(), zeroBaseUnitsDim())

def newPt(theP, incX=None, incY=None):
    """Returns a new Pt object by incrementing existing point incX, incY
    that are both Dim() objects or None."""
    newX = theP.x
    if incX is not None:
        newX += incX
    newY = theP.y
    if incY is not None:
        newY += incY
    return Pt(x=newX, y=newY)

def convertPt(theP, theUnits):
    """Returns a new point with the dimensions of theP converted to theUnits."""
    return Pt(
        x=Dim(convert(theP.x.value, theP.x.units, theUnits), theUnits),
        y=Dim(convert(theP.y.value, theP.y.units, theUnits), theUnits),
        )
    
###########################################
# End: Helper functions for object creation
###########################################
