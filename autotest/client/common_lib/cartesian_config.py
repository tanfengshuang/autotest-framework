#!/usr/bin/python
"""
Cartesian configuration format file parser.

 Filter syntax:
 , means OR
 .. means AND
 . means IMMEDIATELY-FOLLOWED-BY

 Example:
 qcow2..Fedora.14, RHEL.6..raw..boot, smp2..qcow2..migrate..ide
 means match all dicts whose names have:
 (qcow2 AND (Fedora IMMEDIATELY-FOLLOWED-BY 14)) OR
 ((RHEL IMMEDIATELY-FOLLOWED-BY 6) AND raw AND boot) OR
 (smp2 AND qcow2 AND migrate AND ide)

 Note:
 'qcow2..Fedora.14' is equivalent to 'Fedora.14..qcow2'.
 'qcow2..Fedora.14' is not equivalent to 'qcow2..14.Fedora'.
 'ide, scsi' is equivalent to 'scsi, ide'.

 Filters can be used in 3 ways:
 only <filter>
 no <filter>
 <filter>:
 The last one starts a conditional block.

@copyright: Red Hat 2008-2011
"""

import re, os, sys, optparse, collections, commands, logging
from distutils import version


class ParserError:
    def __init__(self, msg, line=None, filename=None, linenum=None):
        self.msg = msg
        self.line = line
        self.filename = filename
        self.linenum = linenum

    def __str__(self):
        if self.line:
            return "%s: %r (%s:%s)" % (self.msg, self.line,
                                       self.filename, self.linenum)
        else:
            return "%s (%s:%s)" % (self.msg, self.filename, self.linenum)


num_failed_cases = 5


class Node(object):
    def __init__(self):
        self.name = []
        self.dep = []
        self.content = []
        self.children = []
        self.labels = set()
        self.append_to_shortname = False
        self.failed_cases = collections.deque()


def _match_adjacent(block, ctx, ctx_set):
    # TODO: explain what this function does
    if block[0] not in ctx_set:
        return 0
    if len(block) == 1:
        return 1
    if block[1] not in ctx_set:
        return int(ctx[-1] == block[0])
    k = 0
    i = ctx.index(block[0])
    while i < len(ctx):
        if k > 0 and ctx[i] != block[k]:
            i -= k - 1
            k = 0
        if ctx[i] == block[k]:
            k += 1
            if k >= len(block):
                break
            if block[k] not in ctx_set:
                break
        i += 1
    return k


def _might_match_adjacent(block, ctx, ctx_set, descendant_labels):
    matched = _match_adjacent(block, ctx, ctx_set)
    for elem in block[matched:]:
        if elem not in descendant_labels:
            return False
    return True


# Filter must inherit from object (otherwise type() won't work)
class Filter(object):
    def __init__(self, s):
        self.filter = []
        for char in s:
            if not (char.isalnum() or char.isspace() or char in ".,_-"):
                raise ParserError("Illegal characters in filter")
        for word in s.replace(",", " ").split():
            word = [block.split(".") for block in word.split("..")]
            for block in word:
                for elem in block:
                    if not elem:
                        raise ParserError("Syntax error")
            self.filter += [word]


    def match(self, ctx, ctx_set):
        for word in self.filter:
            for block in word:
                if _match_adjacent(block, ctx, ctx_set) != len(block):
                    break
            else:
                return True
        return False


    def might_match(self, ctx, ctx_set, descendant_labels):
        for word in self.filter:
            for block in word:
                if not _might_match_adjacent(block, ctx, ctx_set,
                                             descendant_labels):
                    break
            else:
                return True
        return False


class NoOnlyFilter(Filter):
    def __init__(self, line):
        Filter.__init__(self, line.split(None, 1)[1])
        self.line = line


class OnlyFilter(NoOnlyFilter):
    def is_irrelevant(self, ctx, ctx_set, descendant_labels):
        return self.match(ctx, ctx_set)


    def requires_action(self, ctx, ctx_set, descendant_labels):
        return not self.might_match(ctx, ctx_set, descendant_labels)


    def might_pass(self, failed_ctx, failed_ctx_set, ctx, ctx_set,
                   descendant_labels):
        for word in self.filter:
            for block in word:
                if (_match_adjacent(block, ctx, ctx_set) >
                    _match_adjacent(block, failed_ctx, failed_ctx_set)):
                    return self.might_match(ctx, ctx_set, descendant_labels)
        return False


class NoFilter(NoOnlyFilter):
    def is_irrelevant(self, ctx, ctx_set, descendant_labels):
        return not self.might_match(ctx, ctx_set, descendant_labels)


    def requires_action(self, ctx, ctx_set, descendant_labels):
        return self.match(ctx, ctx_set)


    def might_pass(self, failed_ctx, failed_ctx_set, ctx, ctx_set,
                   descendant_labels):
        for word in self.filter:
            for block in word:
                if (_match_adjacent(block, ctx, ctx_set) <
                    _match_adjacent(block, failed_ctx, failed_ctx_set)):
                    return not self.match(ctx, ctx_set)
        return False


class Condition(NoFilter):
    def __init__(self, line):
        Filter.__init__(self, line.rstrip(":"))
        self.line = line
        self.content = []


class NegativeCondition(OnlyFilter):
    def __init__(self, line):
        Filter.__init__(self, line.lstrip("!").rstrip(":"))
        self.line = line
        self.content = []


class Parser(object):
    """
    Parse an input file or string that follows the Cartesian Config File format
    and generate a list of dicts that will be later used as configuration
    parameters by autotest tests that use that format.

    @see: http://autotest.kernel.org/wiki/CartesianConfig
    """

    def __init__(self, filename=None, debug=False):
        """
        Initialize the parser and optionally parse a file.

        @param filename: Path of the file to parse.
        @param debug: Whether to turn on debugging output.
        """
        self.node = Node()
        self.debug = debug
        if filename:
            self.parse_file(filename)


    def parse_file(self, filename):
        """
        Parse a file.

        @param filename: Path of the configuration file.
        """
        self.node = self._parse(FileReader(filename), self.node)


    def parse_string(self, s):
        """
        Parse a string.

        @param s: String to parse.
        """
        self.node = self._parse(StrReader(s), self.node)


    def get_dicts(self, node=None, ctx=[], content=[], shortname=[], dep=[]):
        """
        Generate dictionaries from the code parsed so far.  This should
        be called after parsing something.

        @return: A dict generator.
        """
        def process_content(content, failed_filters):
            # 1. Check that the filters in content are OK with the current
            #    context (ctx).
            # 2. Move the parts of content that are still relevant into
            #    new_content and unpack conditional blocks if appropriate.
            #    For example, if an 'only' statement fully matches ctx, it
            #    becomes irrelevant and is not appended to new_content.
            #    If a conditional block fully matches, its contents are
            #    unpacked into new_content.
            # 3. Move failed filters into failed_filters, so that next time we
            #    reach this node or one of its ancestors, we'll check those
            #    filters first.
            for t in content:
                filename, linenum, obj = t
                if type(obj) is Op:
                    new_content.append(t)
                    continue
                # obj is an OnlyFilter/NoFilter/Condition/NegativeCondition
                if obj.requires_action(ctx, ctx_set, labels):
                    # This filter requires action now
                    if type(obj) is OnlyFilter or type(obj) is NoFilter:
                        self._debug("    filter did not pass: %r (%s:%s)",
                                    obj.line, filename, linenum)
                        failed_filters.append(t)
                        return False
                    else:
                        self._debug("    conditional block matches: %r (%s:%s)",
                                    obj.line, filename, linenum)
                        # Check and unpack the content inside this Condition
                        # object (note: the failed filters should go into
                        # new_internal_filters because we don't expect them to
                        # come from outside this node, even if the Condition
                        # itself was external)
                        if not process_content(obj.content,
                                               new_internal_filters):
                            failed_filters.append(t)
                            return False
                        continue
                elif obj.is_irrelevant(ctx, ctx_set, labels):
                    # This filter is no longer relevant and can be removed
                    continue
                else:
                    # Keep the filter and check it again later
                    new_content.append(t)
            return True

        def might_pass(failed_ctx,
                       failed_ctx_set,
                       failed_external_filters,
                       failed_internal_filters):
            for t in failed_external_filters:
                if t not in content:
                    return True
                filename, linenum, filter = t
                if filter.might_pass(failed_ctx, failed_ctx_set, ctx, ctx_set,
                                     labels):
                    return True
            for t in failed_internal_filters:
                filename, linenum, filter = t
                if filter.might_pass(failed_ctx, failed_ctx_set, ctx, ctx_set,
                                     labels):
                    return True
            return False

        def add_failed_case():
            node.failed_cases.appendleft((ctx, ctx_set,
                                          new_external_filters,
                                          new_internal_filters))
            if len(node.failed_cases) > num_failed_cases:
                node.failed_cases.pop()

        node = node or self.node
        # Update dep
        for d in node.dep:
            dep = dep + [".".join(ctx + [d])]
        # Update ctx
        ctx = ctx + node.name
        ctx_set = set(ctx)
        labels = node.labels
        # Get the current name
        name = ".".join(ctx)
        if node.name:
            self._debug("checking out %r", name)
        # Check previously failed filters
        for i, failed_case in enumerate(node.failed_cases):
            if not might_pass(*failed_case):
                self._debug("    this subtree has failed before")
                del node.failed_cases[i]
                node.failed_cases.appendleft(failed_case)
                return
        # Check content and unpack it into new_content
        new_content = []
        new_external_filters = []
        new_internal_filters = []
        if (not process_content(node.content, new_internal_filters) or
            not process_content(content, new_external_filters)):
            add_failed_case()
            return
        # Update shortname
        if node.append_to_shortname:
            shortname = shortname + node.name
        # Recurse into children
        count = 0
        for n in node.children:
            for d in self.get_dicts(n, ctx, new_content, shortname, dep):
                count += 1
                yield d
        # Reached leaf?
        if not node.children:
            self._debug("    reached leaf, returning it")
            d = {"name": name, "dep": dep, "shortname": ".".join(shortname)}
            for filename, linenum, op in new_content:
                op.apply_to_dict(d)
            yield d
        # If this node did not produce any dicts, remember the failed filters
        # of its descendants
        elif not count:
            new_external_filters = []
            new_internal_filters = []
            for n in node.children:
                (failed_ctx,
                 failed_ctx_set,
                 failed_external_filters,
                 failed_internal_filters) = n.failed_cases[0]
                for obj in failed_internal_filters:
                    if obj not in new_internal_filters:
                        new_internal_filters.append(obj)
                for obj in failed_external_filters:
                    if obj in content:
                        if obj not in new_external_filters:
                            new_external_filters.append(obj)
                    else:
                        if obj not in new_internal_filters:
                            new_internal_filters.append(obj)
            add_failed_case()


    def _debug(self, s, *args):
        if self.debug:
            s = "DEBUG: %s" % s
            print s % args


    def _warn(self, s, *args):
        s = "WARNING: %s" % s
        print s % args


    def _parse_variants(self, cr, node, prev_indent=-1):
        """
        Read and parse lines from a FileReader object until a line with an
        indent level lower than or equal to prev_indent is encountered.

        @param cr: A FileReader/StrReader object.
        @param node: A node to operate on.
        @param prev_indent: The indent level of the "parent" block.
        @return: A node object.
        """
        node4 = Node()

        while True:
            line, indent, linenum = cr.get_next_line(prev_indent)
            if not line:
                break

            name, dep = map(str.strip, line.lstrip("- ").split(":", 1))
            for char in name:
                if not (char.isalnum() or char in "@._-"):
                    raise ParserError("Illegal characters in variant name",
                                      line, cr.filename, linenum)
            for char in dep:
                if not (char.isalnum() or char.isspace() or char in ".,_-"):
                    raise ParserError("Illegal characters in dependencies",
                                      line, cr.filename, linenum)

            node2 = Node()
            node2.children = [node]
            node2.labels = node.labels

            node3 = self._parse(cr, node2, prev_indent=indent)
            node3.name = name.lstrip("@").split(".")
            node3.dep = dep.replace(",", " ").split()
            node3.append_to_shortname = not name.startswith("@")

            node4.children += [node3]
            node4.labels.update(node3.labels)
            node4.labels.update(node3.name)

        return node4


    def _parse(self, cr, node, prev_indent=-1):
        """
        Read and parse lines from a StrReader object until a line with an
        indent level lower than or equal to prev_indent is encountered.

        @param cr: A FileReader/StrReader object.
        @param node: A Node or a Condition object to operate on.
        @param prev_indent: The indent level of the "parent" block.
        @return: A node object.
        """
        while True:
            line, indent, linenum = cr.get_next_line(prev_indent)
            if not line:
                break

            words = line.split(None, 1)

            # Parse 'variants'
            if line == "variants:":
                # 'variants' is not allowed inside a conditional block
                if (isinstance(node, Condition) or
                    isinstance(node, NegativeCondition)):
                    raise ParserError("'variants' is not allowed inside a "
                                      "conditional block",
                                      None, cr.filename, linenum)
                node = self._parse_variants(cr, node, prev_indent=indent)
                continue

            # Parse 'include' statements
            if words[0] == "include":
                if len(words) < 2:
                    raise ParserError("Syntax error: missing parameter",
                                      line, cr.filename, linenum)
                filename = os.path.expanduser(words[1])
                if isinstance(cr, FileReader) and not os.path.isabs(filename):
                    filename = os.path.join(os.path.dirname(cr.filename),
                                            filename)
                if not os.path.isfile(filename):
                    self._warn("%r (%s:%s): file doesn't exist or is not a "
                               "regular file", line, cr.filename, linenum)
                    continue
                node = self._parse(FileReader(filename), node)
                continue

            # Parse 'only' and 'no' filters
            if words[0] in ("only", "no"):
                if len(words) < 2:
                    raise ParserError("Syntax error: missing parameter",
                                      line, cr.filename, linenum)
                try:
                    if words[0] == "only":
                        f = OnlyFilter(line)
                    elif words[0] == "no":
                        f = NoFilter(line)
                except ParserError, e:
                    e.line = line
                    e.filename = cr.filename
                    e.linenum = linenum
                    raise
                node.content += [(cr.filename, linenum, f)]
                continue

            # Look for operators
            op_match = _ops_exp.search(line)

            # Parse conditional blocks
            if ":" in line:
                index = line.index(":")
                if not op_match or index < op_match.start():
                    index += 1
                    cr.set_next_line(line[index:], indent, linenum)
                    line = line[:index]
                    try:
                        if line.startswith("!"):
                            cond = NegativeCondition(line)
                        else:
                            cond = Condition(line)
                    except ParserError, e:
                        e.line = line
                        e.filename = cr.filename
                        e.linenum = linenum
                        raise
                    self._parse(cr, cond, prev_indent=indent)
                    node.content += [(cr.filename, linenum, cond)]
                    continue

            # Parse regular operators
            if not op_match:
                raise ParserError("Syntax error", line, cr.filename, linenum)
            node.content += [(cr.filename, linenum, Op(line, op_match))]

        return node


# Assignment operators

_reserved_keys = set(("name", "shortname", "dep"))


def _op_set(d, key, value):
    if key not in _reserved_keys:
        d[key] = value


def _op_append(d, key, value):
    if key not in _reserved_keys:
        d[key] = d.get(key, "") + value


def _op_prepend(d, key, value):
    if key not in _reserved_keys:
        d[key] = value + d.get(key, "")


def _op_regex_set(d, exp, value):
    exp = re.compile("%s$" % exp)
    for key in d:
        if key not in _reserved_keys and exp.match(key):
            d[key] = value


def _op_regex_append(d, exp, value):
    exp = re.compile("%s$" % exp)
    for key in d:
        if key not in _reserved_keys and exp.match(key):
            d[key] += value


def _op_regex_prepend(d, exp, value):
    exp = re.compile("%s$" % exp)
    for key in d:
        if key not in _reserved_keys and exp.match(key):
            d[key] = value + d[key]


def _op_regex_del(d, empty, exp):
    exp = re.compile("%s$" % exp)
    for key in d.keys():
        if key not in _reserved_keys and exp.match(key):
            del d[key]


_ops = {"=": (r"\=", _op_set),
        "+=": (r"\+\=", _op_append),
        "<=": (r"\<\=", _op_prepend),
        "?=": (r"\?\=", _op_regex_set),
        "?+=": (r"\?\+\=", _op_regex_append),
        "?<=": (r"\?\<\=", _op_regex_prepend),
        "del": (r"^del\b", _op_regex_del)}

_ops_exp = re.compile("|".join([op[0] for op in _ops.values()]))


class Op(object):
    def __init__(self, line, m):
        self.func = _ops[m.group()][1]
        self.key = line[:m.start()].strip()
        value = line[m.end():].strip()
        if value and (value[0] == value[-1] == '"' or
                      value[0] == value[-1] == "'"):
            value = value[1:-1]
        self.value = value


    def apply_to_dict(self, d):
        self.func(d, self.key, self.value)


# StrReader and FileReader

class StrReader(object):
    """
    Preprocess an input string for easy reading.
    """
    def __init__(self, s):
        """
        Initialize the reader.

        @param s: The string to parse.
        """
        self.filename = "<string>"
        self._lines = []
        self._line_index = 0
        self._stored_line = None
        for linenum, line in enumerate(s.splitlines()):
            line = line.rstrip().expandtabs()
            stripped_line = line.lstrip()
            indent = len(line) - len(stripped_line)
            if (not stripped_line
                or stripped_line.startswith("#")
                or stripped_line.startswith("//")):
                continue
            self._lines.append((stripped_line, indent, linenum + 1))


    def get_next_line(self, prev_indent):
        """
        Get the next line in the current block.

        @param prev_indent: The indentation level of the previous block.
        @return: (line, indent, linenum), where indent is the line's
            indentation level.  If no line is available, (None, -1, -1) is
            returned.
        """
        if self._stored_line:
            ret = self._stored_line
            self._stored_line = None
            return ret
        if self._line_index >= len(self._lines):
            return None, -1, -1
        line, indent, linenum = self._lines[self._line_index]
        if indent <= prev_indent:
            return None, -1, -1
        self._line_index += 1
        return line, indent, linenum


    def set_next_line(self, line, indent, linenum):
        """
        Make the next call to get_next_line() return the given line instead of
        the real next line.
        """
        line = line.strip()
        if line:
            self._stored_line = line, indent, linenum


class FileReader(StrReader):
    """
    Preprocess an input file for easy reading.
    """
    def __init__(self, filename):
        """
        Initialize the reader.

        @parse filename: The name of the input file.
        """
        StrReader.__init__(self, open(filename).read())
        self.filename = filename


def get_host_distribution(os_distributions):
    """
    Get the host distribution category
 
    @os_distributions: String with the pattern and distribution name
    @return: None or distribution name
    """
    s, o = commands.getstatusoutput("cat /etc/issue")
    if s != 0:
        logging.warning("Can not get host distribution.")
        os_distribution = None
 
    dict_os = {}
    for i in re.split(";", os_distributions):
        dict_os[re.split(":", i)[0]] = re.split(":", i)[1]
 
    for keys in dict_os:
        distribution = re.findall(keys, o)
        if distribution:
            os_distribution = dict_os[distribution[0]]
            logging.debug("Host distribution is %s" % os_distribution)
            break;
        else:
            logging.warning("Distribution don't fit")
            os_distribution = None
    return os_distribution


def get_host_verson(dict_test):
    """
    Get host version by kernel version
    
    @dict_test: one dict of the list test cases
    @return: host version category
    """
    print dict_test.get("OS_distributions")
    os_distribution = get_host_distribution(dict_test.get("OS_distributions"))
    if os_distribution:
       s, o = commands.getstatusoutput("uname -r")
       if s != 0:
           logging.warning("Can not get kernel version")
           host_version = None
       else:
           cur_v = version.LooseVersion(o)
           hvs = dict_test.get("%s_version_standard" % os_distribution)
           v_dict = {}
           for i in re.split(";", hvs):
               v_dict[re.split(":", i)[1]] = re.split(":", i)[0]
 
           v_list = sorted(v_dict.items()
                           ,key=lambda v_dict:version.LooseVersion(v_dict[0]))
 
           if cur_v < version.LooseVersion(v_list[0][0]):
               logging.warning("Old version of %s" % os_distribution)
               host_version = None
           elif cur_v > version.LooseVersion(v_list[-1][0]):
               host_version = v_list[-1][1]
           else:
               count = 1
               while count < len(v_list):
                   if cur_v >= version.LooseVersion(v_list[count-1][0]) and\
                      cur_v <= version.LooseVersion(v_list[count][0]):
                       host_version = v_list[count-1][1]
                       break;
                   elif cur_v >= version.LooseVersion(v_list[count][0]):
                       count += 1
           if host_version:
                logging.debug("Host kernel version is %s" % host_version)
    else:
        host_version = None
    return host_version

def get_image_filename(params, root_dir):
    """
    Generate an image path from params and root_dir.

    @param params: Dictionary containing the test parameters.
    @param root_dir: Base directory for relative filenames.

    @note: params should contain:
           image_name -- the name of the image file, without extension
           image_format -- the format of the image (qcow2, raw etc)
    """
    image_name = params.get("image_name", "image")
    image_format = params.get("image_format", "qcow2")
    if params.get("use_storage") == "iscsi":
        return image_name
    if params.get("image_raw_device") == "yes":
        return image_name
    image_filename = "%s.%s" % (image_name, image_format)
    image_filename = os.path.join(root_dir, image_filename)
    return image_filename


if __name__ == "__main__":
    parser = optparse.OptionParser('usage: %prog [options] filename '
                                   '[extra code] ...\n\nExample:\n\n    '
                                   '%prog tests.cfg "only my_set" "no qcow2"')
    parser.add_option("-v", "--verbose", dest="debug", action="store_true",
                      help="include debug messages in console output")
    parser.add_option("-f", "--fullname", dest="fullname", action="store_true",
                      help="show full dict names instead of short names")
    parser.add_option("-c", "--contents", dest="contents", action="store_true",
                      help="show dict contents")

    options, args = parser.parse_args()
    if not args:
        parser.error("filename required")

    c = Parser(args[0], debug=options.debug)
    # Get host version related parameters
    host_tmp = {}
    for i in c.get_dicts():
        host_tmp = i
    if len(host_tmp) > 0:
        host_version = get_host_verson(host_tmp)
        str = ""
        if host_version:
            str += "only %s_host\n" % host_version
        else:
            str += "only default_host"
        c.parse_string(str)

    for s in args[1:]:
        c.parse_string(s)
    test_dicts = list(c.get_dicts())
    if len(test_dicts) > 0 and "prepare_case" in test_dicts[0].keys():
        prepare_case = test_dicts[0]["prepare_case"].split()
    else:
        prepare_case = ['unattended_install', 'rh_kernel_update',
                                           'disable_win_update']
    for case in prepare_case:
        del_list = {}
        for d in test_dicts:
            if case in d["name"]:
                if "case_type" in d.keys() and d["case_type"] == "prepare":
                    img_name = get_image_filename(d, ".")
                    if img_name not in del_list.keys():
                        del_list[img_name] = [d]
                    else:
                        del_list[img_name].append(d)
        for img_l in del_list.keys():
            if len(del_list[img_l]) > 1:
                for d in del_list[img_l][:-1]:
                    test_dicts.remove(d)
    for i in range(len(test_dicts)):
        if options.fullname:
            print "dict %4d:  %s" % (i + 1, test_dicts[i]["name"])
        else:
            print "dict %4d:  %s" % (i + 1, test_dicts[i]["shortname"])
        if options.contents:
            keys = test_dicts[i].keys()
            keys.sort()
            for key in keys:
                print "    %s = %s" % (key, test_dicts[i][key])
