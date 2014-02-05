# ctags generated by the command:
# ctags -R --sort=yes --c++-kinds=cf --fields=aiksz --language-force=C++
# --exclude=*.in --exclude=*.java --exclude=*.py --exclude=*.js --exclude=*.bmp
# -f vtk ~/Projects/vtk/src

import distutils.spawn
import os.path
import re
import shutil
import subprocess
import sys
import tempfile

try:
    import argparse
except ImportError:
    import _argparse as argparse

tagMatcherType = re.compile('^(.+)\t(\S+)\t/\^(.*)\$/;"\t(.*)\n')

class Tag:
    def __init__(self):
        self._name = None
        self._access = None
        self._kind = None
        self._fyle = None
        self._decl = None
        self._class = None
        self._inherits = None

    def __repr__(self):
        return "<Tag %s in file %s>" % (self.name, self.fyle)

    def parse(self, line):
        """
        Parse a CTags line and set myself from it.
        """
        # example of CTags lines:

# Type1: ARangeFunctor /home/sankhesh/Projects/vtk/src/Common/Core/Testing/Cxx/TestSMP.cxx /^class ARangeFunctor$/;" kind:c

# Type2: APIDiagram  /home/sankhesh/Projects/vtk/src/Charts/Core/Testing/Cxx/TestDiagram.cxx /^class APIDiagram : public vtkContextItem$/;"  kind:c  inherits:vtkContextItem

# Type3: AbortFlagOff /home/sankhesh/Projects/vtk/src/Common/Core/vtkCommand.h  /^  void AbortFlagOff()$/;" kind:f  class:vtkCommand  access:public

# Type4: BooleanSet     /home/sankhesh/Projects/vtk/src/Filters/General/vtkMultiThreshold.h     /^  class BooleanSet : public Set {$/;" kind:c  class:vtkMultiThreshold inherits:Set    access:public

        tag = tagMatcherType.search(line)
        if not tag:
            raise KeyError, "line %s is not an expected ctags line" %line

        self._name = tag.expand('\\1').strip()
        self._fyle = tag.expand('\\2').strip()
        self._decl = tag.expand('\\3').strip()
        exts = tag.expand('\\4').strip().split('\t')
        for ext in exts:
            pre = ext.strip().split(':')[0]
            suf = ext.strip().split(':')[1]
            if pre == 'kind':
                self._kind = suf
                continue
            if pre == 'class' or pre == 'struct':
                self._class = suf
                continue
            if pre == 'access':
                self._access = suf
                continue
            if pre == 'inherits':
                self._inherits = suf
                continue

class CTags():

    def __init__(self):
        self._tagFile = "" # path to tag file
        self._classes = []
        self._pub_methods = []

    def set_tag_file(self, path):
        """
        Parse tags from the given file.
        """
        handle = open(path, "r")
        self._parse(handle.readlines())

    def _parse(self, lines):
        for line in lines:
            if line.startswith('!_TAG_'):
                continue
            if line.startswith('ctags: Warning: ignoring null tag'):
                continue

            t = Tag()
            t.parse(line)

       # Now make append to list of classes and public methods
            if t._kind == 'c':
                self._classes.append(t._name)
            if t._kind == 'f' and t._access == 'public':
                met = t._class + ":" + t._name
                self._pub_methods.append(met)

class CompareVersions():
    def __init__(self, src_dir, version1, version2, tmp_dir):
        self.tmp_dir = os.path.abspath(tmp_dir)
        self.src_dir = self.tmp_dir + os.sep + os.path.basename(src_dir)
        self.src_work_dir = os.path.abspath(src_dir)
        self.version1 = version1
        self.version2 = version2
        self.classes_removed = []
        self.classes_added = []
        self.pub_methods_removed = []
        self.pub_methods_added = []
        self.tag_f1 = None
        self.tag_f2 = None
        self._git_HEAD = None
        self._git_diff = None
        # Get system executable paths for git and ctags
        self.svar = SystemVar()
        # Setup the temporary working tree
        self.setup_src_dir()
        # Compare the two versions provided
        self.generate_ctags()
        self.get_diff()

    def get_diff(self):
        print "Parsing tag file %s..." % self.tag_f1
        T1 = CTags()
        T1.set_tag_file(self.tag_f1)
        print "Parsing tag file %s...Done" % self.tag_f1
        print "Parsing tag file %s..." % self.tag_f2
        T2 = CTags()
        T2.set_tag_file(self.tag_f2)
        print "Parsing tag file %s...Done" % self.tag_f2
        self.classes_added = list(set(T2._classes) - set(T1._classes))
        self.classes_removed = list(set(T1._classes) - set(T2._classes))
        self.pub_methods_added = list(set(T2._pub_methods) - set(T1._pub_methods))
        self.pub_methods_removed = list(set(T1._pub_methods) - set(T2._pub_methods))

    def git_checkout_version(self, ver):
        git_cmd = self.svar.git_exe + ' --git-dir=' + self.src_dir + os.sep + '.git --work-tree=' +\
            self.src_dir
        # Make sure working tree does not have any local modifications
        git_modified = git_cmd + ' ls-files -m'
        git_m_proc = subprocess.Popen(git_modified.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        git_m_proc.wait()
        git_m_proc_stdout = git_m_proc.stdout.read()
        if git_m_proc_stdout:
            print "Working tree has local modifications."
            print "Please commit or reset the following files:"
            print git_m_proc_stdout
            sys.exit(1)

        # Reset the working tree to version specified
        git_reset_cmd = git_cmd + ' reset -q --hard ' + ver
        git_proc = subprocess.Popen(git_reset_cmd.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        git_proc.wait()
        git_proc_stderr = git_proc.stderr.read()
        if git_proc_stderr:
            print "Error while git reset to version:", ver
            print git_proc_stderr
            sys.exit(1)

    def create_tagfile(self, src_dir, fname):
        ctags_proc = subprocess.Popen([self.svar.ctags_exe, '-R', '--sort=yes',
            '--c++-kinds=cf', '--fields=aiksz', '--language-force=C++',
            '--exclude=*.in', '--exclude=*.java', '--exclude=*.py',
            '--exclude=*.js', '--exclude=*.bmp', '-f', fname, src_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ctags_proc.wait()
        ctags_proc_stderr = ctags_proc.stderr.read()
        if ctags_proc_stderr:
            print "Error while creating tagfile with ctags:", fname
            print ctags_proc_stderr
            sys.exit(1)

    def generate_ctags(self):
        # Store the current HEAD SHA-1 sum
        print "Getting the SHA-1 sum of HEAD of current working tree..."
        self._git_HEAD = self.git_current_version(self.src_dir)
        print "Getting the SHA-1 sum of HEAD of current working tree... %s" %\
            self._git_HEAD
        # Reset working tree to version1
        print "Checking out version %s..." % self.version1
        self.git_checkout_version(self.version1)
        # Create tag file for version1
        self.tag_f1 = self.gen_tagfile_name(self.version1)
        print "Creating tagfile (%s) for version %s..." % (self.tag_f1,
                self.version1)
        self.create_tagfile(self.src_dir, self.tag_f1)
        print "Creating tagfile (%s) for version %s...Done" % (self.tag_f1,
                self.version1)
        # Reset working tree to version2
        print "Checking out version %s..." % self.version2
        self.git_checkout_version(self.version2)
        # Create tag file for version2
        self.tag_f2 = self.gen_tagfile_name(self.version2)
        print "Creating tagfile (%s) for version %s..." % (self.tag_f2,
                self.version2)
        self.create_tagfile(self.src_dir, self.tag_f2)
        print "Creating tagfile (%s) for version %s...Done" % (self.tag_f2,
                self.version2)

    def gen_tagfile_name(self, ver):
        tag_f_name = self.tmp_dir + os.sep + os.path.basename(self.src_dir) +\
                "_" + ver + '.ctags'
        return tag_f_name

    def git_current_version(self, src_dir):
        git_cmd = self.svar.git_exe + ' --git-dir=' + src_dir + os.sep +\
                '.git --work-tree=' + src_dir + ' rev-parse HEAD'
        git_proc = subprocess.Popen(git_cmd.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        git_proc.wait()
        git_proc_stderr = git_proc.stderr.read()
        if git_proc_stderr:
            print "Error while getting current HEAD SHA-1 sum:"
            print git_proc_stderr
            sys.exit(1)
        return git_proc.stdout.read()

    def git_diff_versions(self):
        git_cmd = self.svar.git_exe + ' --git-dir=' + src_dir + os.sep +\
                '.git --work-tree=' + src_dir + ' diff ' + self.version1 +\
                '..' + self.version2
        git_proc = subprocess.Popen(git_cmd.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        git_proc.wait()
        git_proc_stderr = git_proc.stderr.read()
        if git_proc_stderr:
            print "Error while getting git diff between versions %s and %s" %\
                (self.version1, self.version2)
            print git_proc_stderr
            sys.exit(1)
        return git_proc.stdout.read()

    def get_deprecated_methods(self):
        self._git_diff = self.git_diff_versions()
        depMatcherType = re.compile('^\+\tVTK_LEGACY_BODY\((.*),"(.*)"')

    def setup_src_dir(self):
        print "Setting up a clone of working tree (%s) in %s..." %\
            (self.src_work_dir, self.src_dir)
        git_cmd = self.svar.git_exe + ' clone -l --no-hardlinks ' +\
            self.src_work_dir + ' ' + self.src_dir
        git_proc = subprocess.Popen(git_cmd.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        git_proc.wait()
        git_proc_stderr = git_proc.stderr.read()
        if git_proc_stderr:
            print "Error while git clone into temporary working directory."
            print "Command Used:", git_cmd
            print git_proc_stderr
            sys.exit(1)
        print "Setting up a clone of working tree (%s) in %s...Done" %\
            (self.src_work_dir, self.src_dir)

    def cleanup(self):
        if os.path.exists(self.tag_f1):
            os.remove(self.tag_f1)
        if os.path.exists(self.tag_f2):
            os.remove(self.tag_f2)
        if os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir)

class SystemVar():
    def __init__(self):
        self.git_exe = None
        self.ctags_exe = None
        self.get_exes()

    def get_exes(self):
        self.git_exe = self.get_exe("git")
        self.ctags_exe = self.get_exe("ctags")

    def get_exe(self, exe):
        exe_file = distutils.spawn.find_executable(exe)
        if not exe_file:
            print "%s not found in system PATH" % exe
            for trial in range(3):
                exe_file = raw_input("Enter full path to %s executable:\n"\
                        % exe)
                if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                    break
                else:
                    print "The provided path is not an executable"
                    exe_file = None
            if not exe_file:
                print "Could not locate %s executable in 3 tries. Exiting..."\
                        % exe
                sys.exit(1)
        return exe_file

def printReport(comp, args):
    if args.wikiOutput:
        print "==API differences when going from version %s to version %s=="\
            %(args.versions[0], args.versions[1])
        print r'{| class="wikitable sortable" border="1" cellpadding="5" '\
            'cellspacing="0"'
        print r'!Classes Added'
        for cls in comp.classes_added:
            print r'|-'
            print r'|%s' %cls
        print r'|}'
        print r'{| class="wikitable sortable" border="1" cellpadding="5" '\
            'cellspacing="0"'
        print r'!Classes Removed'
        for cls in comp.classes_removed:
            print r'|-'
            print r'|%s' %cls
        print r'|}'
        print r'{| class="wikitable sortable" border="1" cellpadding="5" '\
            'cellspacing="0"'
        print r'!Public Methods Added'
        for cls in comp.pub_methods_added:
            print r'|-'
            print r'|%s' %cls
        print r'|}'
        print r'{| class="wikitable sortable" border="1" cellpadding="5" '\
            'cellspacing="0"'
        print r'!Public Methods Removed'
        for cls in comp.pub_methods_removed:
            print r'|-'
            print r'|%s' %cls
        print r'|}'
    else:
        print "-------------------- REPORT --------------------"
        print "==API differences when going from version %s to version %s=="\
            %(args.versions[0], args.versions[1])
        print "~~~~~~~~~~~~~~~~Classes Added~~~~~~~~~~~~~~~~~~~"
        for cls in comp.classes_added:
            print cls
        print "~~~~~~~~~~~~~~~Classes Removed~~~~~~~~~~~~~~~~~~"
        for cls in comp.classes_removed:
            print cls
        print "~~~~~~~~~~~~~Public Methods Added~~~~~~~~~~~~~~~"
        for cls in comp.pub_methods_added:
            print cls
        print "~~~~~~~~~~~~Public Methods Removed~~~~~~~~~~~~~~"
        for cls in comp.pub_methods_removed:
            print cls


def start(args):
    # Create a clone of the current working tree in temp dir
    C = CompareVersions(args.src[0], args.versions[0], args.versions[1],
            args.tmp)
    printReport(C, args)
    if not args.dontClean:
        C.cleanup()
    else:
        # Restore the working directory to its original state
        C.git_checkout_version(C._git_HEAD)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare two different'\
        ' revisions of a C++ source tree under GIT revision control')
    parser.add_argument("src", type=str, nargs=1,
        help="Path to the working directory")
    parser.add_argument("versions", type=str, nargs=2,
        help="Two versions to compare. (SHA/branch/tag)")
    parser.add_argument("-t", "--tmp", type=str,
        default=tempfile.gettempdir(),
        help="Path to a temporary directory where the current working tree"\
             " can be cloned.(default: System Temp Directory")
    parser.add_argument("-w", "--wikiOutput", action='store_true',
        help="Print output with wiki markup.")
    parser.add_argument("-d", "--dontClean", action='store_true',
        help="Do not delete temporary files and directories.")

    args = parser.parse_args()
    start(args)
