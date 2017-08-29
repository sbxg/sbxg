# Copyright (c) 2017 Jean Guyomarc'h
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import abc

class SbxgError(Exception):
    """
    Super class, used by exception handlers to filter-out SBXG-related
    exceptions.
    """
    pass

class InvalidToolchain(SbxgError):
    def __init__(self, expected_arch, toolchain_arch):
        self.expected_arch = expected_arch
        self.toolchain_arch = toolchain_arch

    def __str__(self):
        return "Invalid toolchain architecture '{}'. '{}' was expected".format(
            self.toolchain_arch, self.expected_arch
        )

class MissingRequiredData(SbxgError):
    def __init__(self, in_file, prop):
        self.in_file = in_file
        self.property = prop 

    def __str__(self):
        return "Missing mandatory property '{}' in '{}'".format(
            self.property, self.in_file
        )

class InvalidFileData(SbxgError):
    def __init__(self, in_file, prop, target):
        self.in_file = in_file
        self.property = prop
        self.target = target

    def __str__(self):
        return "Cannot find file '{}' requested by property '{}' from file '{}'".format(
            self.target, self.property, self.in_file
        )


class InvalidKernelType(SbxgError):
    def __init__(self, config_file, found_type, expected_types):
        self.config_file = config_file
        self.found_type = found_type
        self.expected_types = expected_types

    def __str__(self):
        return "Kernel type '{}' deduced from file '{}' is not one of '{}'".format(
            self.found_type, self.config_file, ' '.join(self.expected_types)
        )

class SbxgTypeError(SbxgError):
    @abc.abstractproperty
    def typename(self):
        pass

    def __init__(self, in_file, prop):
        self.in_file = in_file
        self.property = prop

    def __str__(self):
        return "Property '{}' in file '{}' is expected to be a list".format(
            self.property, self.in_file
        )

class NotAList(SbxgTypeError):
    def typename(self):
        return "list"

class NotAString(SbxgTypeError):
    def typename(self):
        return "string"
