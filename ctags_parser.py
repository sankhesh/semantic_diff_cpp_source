import re

tagMatcherType1 = re.compile('^(.+)\t(\S+)\t(.*);"\t(\S+)\n')
tagMatcherType2 = re.compile('^(.+)\t(\S+)\t(.*);"\t(\S+)\t(\S+)\n')

class Tag:
    name = None
    access = None
    kind = None
    klazz = None
    fyle = None

    def __repr__(self):
        return "<Tag %s in file %s>" % (self.name, self.fyle)

    def parse(self, line):
        """
        Parse a CTags line and set myself from it.
        """
        # example of CTags lines:
        # Type1: ARangeFunctor /home/sankhesh/Projects/vtk/src/Common/Core/Testing/Cxx/TestSMP.cxx /^class ARangeFunctor$/;" kind:c
        # Type2: AbortFlagOff  /home/sankhesh/Projects/vtk/src/Common/Core/vtkCommand.h  /^  void AbortFlagOff()$/;" kind:f  access:public
        t = tagMatcherType1.search(line)
        # If this is a type 1 tag
        if t:

        # else if it is a member
        else:
            t = tagMatcherType2.search(line)

