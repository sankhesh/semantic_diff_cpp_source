"""
Code to parse ctags files.
"""

import re

try:
    import argparse
except ImportError:
    import _argparse as argparse


# see man ctags, TAG FILE FORMAT
#tagMatcher = re.compile('^(.+)\t(\S+)\t(.*);"\t(\S)\t(.*)')
tagMatcher = re.compile('^(.+)\t(\S+)\t(.*);"\t(.*)\n')
#tagMatcher = re.compile('^(.+)\t(\S+)\t(.*);(.*)\n')

class Tag:
    """
    I represent one line in a ctags file.
    """
    name = None
    file = None
    line = None
    language = None
    klazz = None

    def __repr__(self):
        return "<Tag %s in file %s>" % (self.name, self.file)

    def parse(self, line):
        """
        Parse a CTags line and set myself from it.
        """
        # example of CTags lines:
        #AMRIndexIterator::GetFlatIndex \t /home/sankhesh/Projects/vtk/src/Common/DataModel/vtkUniformGridAMRDataIterator.cxx \t /^  virtual unsigned int GetFlatIndex() { return this->Index;}$/;" \t access:public
        # pads_cookie     gst/gstelement.h        /^  guint32               pads_cookie;$/;"      m       line:438        language:C++    struct:_GstElement
        # target_state    gst/gstelement.h        /^      GstState              target_state;$/;" m       line:444        language:C++    struct:_GstElement::<anonymous>::<anonymous>

        m = tagMatcher.search(line)
        if not m:
            raise KeyError, "line %s not a ctags line" % line

        kind = m.expand('\\4') # e.g. m for member, i for namespace
        # ignore namespace, since they map to things like import
        if kind == 'i':
            return

        self.name = m.expand('\\1')
        self.file = m.expand('\\2')

#        extended = m.expand('\\5')
#        for ext in extended.split('\t'):
#            tags = ext.split(':')
#            key = tags[0]
#            value = tags[1]
#
#            if key == 'line':
#                self.line = int(value)
#            elif key == 'language':
#                self.language = value
#            elif key == 'class':
#                self.klazz = value

class CTags():

    def __init__(self):
        self._files = {} # path -> dict of line number -> tag

    def addFile(self, path):
        """
        Parse tags from the given file and add.
        """
        handle = open(path, "r")
        self._parse(handle.readlines())

    def addString(self, string):
        if not string:
            return
        self._parse(string.split('\n'))

    def _parse(self, lines):
        for line in lines:
            if line.startswith('!_TAG_'):
                continue
            if line.startswith('$'):
                continue
            if line.startswith('ctags: Warning: ignoring null tag'):
                continue

            t = Tag()
            t.parse(line)
            if not self._files.has_key(t.file):
                self._files[t.file] = {}
            self._files[t.file][t.line] = t

    def getTags(self, file, line, count=1):
        """
        Get all tags for the given file, starting at the given line number,
        covered by the given count of lines from that point.

        @returns: list of L{Tag}
        """
        ret = []
        if count < 1:
            return ret

        tags = self._files[file]
        starts = tags.keys()
        starts.sort()
        i = 0
        # look for the tag right before the given line number
        while tags[starts[i]].line <= line:
            i += 1
            if i == len(starts):
                # line number is past the last tag, so we only return
                # the last tag
                self.debug('Returning only tag starting on %d' % starts[-1])
                return [tags[starts[-1]], ]

        # now i points to a tag on or beyond the given line number, so go back
        # one
        i -= 1
            
        if i >= 0:
            # there is in fact a tag started before the given line, so append it
            startLine = starts[i]
            t = tags[startLine]
            self.debug('appending tag for %s starting on line %d' % (
                t.name, startLine))
            ret.append(t)

        # now we go back to the first tag starting on or past the given line
        # number
        i += 1

        # now find all tags in the given range and append
        # it is possible we are already past the end of starts
        while count > 1 and tags[starts[i]].line < line + count:
            startLine = starts[i]
            t = tags[startLine]
            self.debug('appending tag for %s starting on line %d' % (
                t.name, startLine))
            ret.append(t)
            i += 1
            if i == len(starts):
                break

        self.debug('returning %d tags' % len(ret))
        return ret

def add_arguments(parser):
    parser.add_argument("-d", "--debug",
        help="log debugging messages to stdout", action="store_true")
    parser.add_argument("-f", "--tagFile", type=str, nargs=1,
        metavar=('ctags'), required=True, help="Tag file to parse")
    return parser

def start(argv=None, description="Get differences in versions"):
    parser = argparse.ArgumentParser(description=description)
    add_arguments(parser)
    args = parser.parse_args(argv)
    T = CTags()
    T.addFile(str(args.tagFile[0]))
    return T.getTags(args.tagFile[0],1)

if __name__ == "__main__":
    start()
