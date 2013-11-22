#!/usr/bin/env python

import clang.cindex
import sys

def find_typerefs(node, typename):
    """ Find all references to the type named 'typename'
    """
    if node.kind.is_reference():
        ref_node = clang.cindex.Cursor_ref(node)
        if ref_node.spelling == typename:
            print 'Found %s [line=%s, col=%s]' %(
                    typename, node.location.line, node.location.column)
    # Recurse for children of this node
    for c in node.get_children():
        find_typerefs(c,typename)

def main():
    index = clang.cindex.Index.create()
    parser = index.parse(sys.argv[1])
    find_typerefs(parser.cursor, sys.argv[2])

if __name__ == "__main__":
    main()
