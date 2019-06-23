# Copyright (c) 2017, 2019 Jean Guyomarc'h
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

import jinja2
import os

class Templater(object):
    def __init__(self, database, search_paths):
        self.database = database
        self.j2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(search_paths),
            lstrip_blocks=True,
            undefined=jinja2.StrictUndefined
        )
        self.j2_env.filters['basename'] = os.path.basename
        self.j2_env.filters['dirname'] = os.path.dirname

    def template_file(self, filename, output_file=None):
        template = self.j2_env.get_template(filename)
        output = template.render(self.database)
        if output_file:
            with open(output_file, 'w') as stream:
                stream.write(output)
        return output
