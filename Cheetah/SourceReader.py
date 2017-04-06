"""
SourceReader class for Cheetah's Parser and CodeGenerator
"""

import re
import sys
unicode = type(u"")

EOLre = re.compile(r'[ \f\t]*(?:\r\n|\r|\n)')
EOLZre = re.compile(r'(?:\r\n|\r|\n|\Z)')
ENCODINGsearch = re.compile("coding[=:]\s*([-\w.]+)").search


class Error(Exception):
    pass


class SourceReader(object):

    def __init__(self, src, filename=None, breakPoint=None, encoding=None):
        self._src = src
        self._filename = filename
        self._srcLen = len(src)
        if breakPoint is None:
            self._breakPoint = self._srcLen
        else:
            self.setBreakPoint(breakPoint)
        self._pos = 0
        self._bookmarks = {}
        self._posTobookmarkMap = {}

        # collect some meta-information
        self._EOLs = []
        pos = 0
        while pos < len(self):
            EOLmatch = EOLZre.search(src, pos)
            self._EOLs.append(EOLmatch.start())
            pos = EOLmatch.end()

        self._BOLs = [self.findBOL(pos) for pos in self._EOLs]

    def src(self):
        return self._src

    def filename(self):
        return self._filename

    def __len__(self):
        return self._breakPoint

    def __getitem__(self, i):
        if isinstance(i, slice):
            start, stop, step = max(i.start, 0), max(i.stop, 0), i.step
            return self._src[start:stop:step]
        else:
            self.checkPos(i if isinstance(i, int) else i.stop)
            return self._src[i]

    def splitlines(self):
        if not hasattr(self, "_srcLines"):
            self._srcLines = self._src.splitlines()
        return self._srcLines

    def lineNum(self, pos=None):
        if pos is None:
            pos = self._pos
        return next((i for i, BOL in enumerate(self._BOLs)
                     if BOL <= pos <= self._EOLs[i]), None)

    def getRowCol(self, pos=None):
        if pos is None:
            pos = self._pos
        line_num = self.lineNum(pos)
        BOL, EOL = self._BOLs[line_num], self._EOLs[line_num]
        return line_num + 1, pos - BOL + 1

    def getRowColLine(self, pos=None):
        if pos is None:
            pos = self._pos
        row, col = self.getRowCol(pos)
        return row, col, self.splitlines()[row-1]

    def getLine(self, pos):
        if pos is None:
            pos = self._pos
        line_num = self.lineNum(pos)
        return self.splitlines()[line_num]

    def pos(self):
        return self._pos

    def setPos(self, pos):
        self.checkPos(pos)
        self._pos = pos

    def validPos(self, pos):
        return 0 <= pos <= self._breakPoint

    def checkPos(self, pos):
        if pos > self._breakPoint:
            raise Error("pos (%d) is invalid: beyond the "
                        "stream's end (%d)" % (pos, self._breakPoint - 1))
        elif pos < 0:
            raise Error("pos (%d) is invalid: less than 0" % pos)

    def breakPoint(self):
        return self._breakPoint

    def setBreakPoint(self, pos):
        if pos > self._srcLen:
            raise Error("New breakpoint (%d) is invalid: beyond the end of "
                        "stream's source string (%d)" % (pos, self._srcLen))
        elif pos < 0:
            raise Error("New breakpoint (%d) is invalid: less than 0" % pos)

        self._breakPoint = pos

    def setBookmark(self, name):
        self._bookmarks[name] = self._pos
        self._posTobookmarkMap[self._pos] = name

    def hasBookmark(self, name):
        return name in self._bookmarks

    def gotoBookmark(self, name):
        if not self.hasBookmark(name):
            raise Error("Invalid bookmark (%s) is invalid: "
                        "does not exist" % name)
        pos = self._bookmarks[name]
        if not self.validPos(pos):
            raise Error("Invalid bookmark (%s, %d) is invalid: "
                        "pos is out of range" % (name, pos))
        self._pos = pos

    def atEnd(self):
        return self._pos >= self._breakPoint

    def atStart(self):
        return self._pos == 0

    def peek(self, offset=0):
        self.checkPos(self._pos + offset)
        pos = self._pos + offset
        return self._src[pos]

    def getc(self):
        pos = self._pos
        if self.validPos(pos + 1):
            self._pos += 1
        return self._src[pos]

    def ungetc(self, c=None):
        if not self.atStart():
            raise Error("Already at beginning of stream")

        self._pos -= 1
        if c is not None:
            self._src[self._pos] = c

    def advance(self, offset=1):
        self.checkPos(self._pos + offset)
        self._pos += offset

    def rev(self, offset=1):
        self.checkPos(self._pos - offset)
        self._pos -= offset

    def read(self, offset):
        self.checkPos(self._pos + offset)
        start = self._pos
        self._pos += offset
        return self._src[start:self._pos]

    def readTo(self, to, start=None):
        self.checkPos(to)
        if start is None:
            start = self._pos
        self._pos = to
        return self._src[start:to]

    def readToEOL(self, start=None, gobble=True):
        EOLmatch = EOLZre.search(self.src(), self.pos())
        pos = EOLmatch.end() if gobble else EOLmatch.start()
        return self.readTo(to=pos, start=start)

    def find(self, it, pos=None):
        if pos is None:
            pos = self._pos
        return self._src.find(it, pos)

    def startswith(self, it, pos=None):
        return self.find(it, pos) == self.pos()

    def rfind(self, it, pos):
        if pos is None:
            pos = self._pos
        return self._src.rfind(it, pos)

    def findBOL(self, pos=None):
        if pos is None:
            pos = self._pos
        src = self.src()
        return max(src.rfind('\n', 0, pos) + 1,
                   src.rfind('\r', 0, pos) + 1, 0)

    def findEOL(self, pos=None, gobble=False):
        if pos is None:
            pos = self._pos
        match = EOLZre.search(self.src(), pos)
        return match.end() if gobble else match.start()

    def isLineClearToPos(self, pos=None):
        if pos is None:
            pos = self.pos()
        self.checkPos(pos)
        src = self.src()
        BOL = self.findBOL()
        return BOL == pos or src[BOL:pos].isspace()

    def matches(self, strOrRE):
        if isinstance(strOrRE, (str, unicode)):
            return self.startswith(strOrRE, pos=self.pos())
        else: # assume an re object
            return strOrRE.match(self.src(), self.pos())

    def matchWhiteSpace(self, WSchars=' \f\t'):
        return (not self.atEnd()) and self.peek() in WSchars

    def getWhiteSpace(self, max=None, WSchars=' \f\t'):
        if not self.matchWhiteSpace(WSchars):
            return ""
        start = self.pos()
        breakPoint = self.breakPoint()
        if max is not None:
            breakPoint = min(breakPoint, self.pos()+max)
        while self.pos() < breakPoint:
            self.advance()
            if not self.matchWhiteSpace(WSchars):
                break
        return self.src()[start:self.pos()]

    def matchNonWhiteSpace(self, WSchars=' \f\t\n\r'):
        return self.atEnd() or not self.peek() in WSchars

    def getNonWhiteSpace(self, WSchars=' \f\t\n\r'):
        if not self.matchNonWhiteSpace(WSchars):
            return ""
        start = self.pos()
        while self.pos() < self.breakPoint():
            self.advance()
            if not self.matchNonWhiteSpace(WSchars):
                break
        return self.src()[start:self.pos()]
