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

import os
import subprocess

class Subcomponent(object):
    def __init__(self, templater, program='subcomponent'):
        self._templater = templater
        self._program = program
        self._text = ""

    def add_components(self, components_names):
        for component_name in components_names:
            self.add_component(component_name)

    def add_component(self, component_name):
        filename = component_name + ".j2"
        self._text += '\n' + self._templater.template_file(filename)

    def call(self, in_directory, **kwargs):

        # Create the directory structure if it does not already exist
        path_dir = os.path.join(in_directory, 'subcomponent')
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        # Generate the main subcomponent file by aggregating all different
        # configurations together.
        path = os.path.join(path_dir, 'components.sub')
        with open(path, 'w') as stream:
            stream.write("subcomponents {")
            stream.write(self._text)
            stream.write("}\n")

        # Subcomponent!
        cmd = [self._program, "-C", in_directory, "fetch"]
        if kwargs.get('no_download') is True:
            cmd.append("--dry-run")
        subprocess.check_call(cmd)
