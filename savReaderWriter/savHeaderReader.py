#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections

from savReaderWriter import *
from header import *

class SavHeaderReader(Header):
    """
    This class contains methods that read the data dictionary of an SPSS
    data file. This yields the same information as the Spss command 'DISPLAY
    DICTIONARY' NB: do not confuse an Spss dictionary with a Python
    dictionary!

    Typical use:
    with SavHeaderReader(savFileName) as spssDict:
        wholeDict = spssDict.dataDictionary()
        print unicode(spssDict)
    """

    def __init__(self, savFileName, ioUtf8=False, ioLocale=None):
        """ Constructor. Initializes all vars that can be recycled """
        super(SavHeaderReader, self).__init__(savFileName, "rb", None,
                                              ioUtf8, ioLocale)
        self.fh = self.openSavFile()
        self.varNames, self.varTypes = self.varNamesTypes
        self.numVars = self.numberofVariables
        self.nCases = self.numberofCases

    def __str__(self):
        """ This function returns a report of the SPSS data dictionary
        (i.e., the header), in the encoding of the spss file"""
        return unicode(self).encode(self.fileEncoding)

    def __unicode__(self):
        """ This function returns a report of the SPSS data dictionary
        (i.e., the header)."""
        report = ""
        if self.textInfo:
            report += self.textInfo + os.linesep
        report += self.reportSpssDataDictionary(self.dataDictionary())
        return report

    def __enter__(self):
        """ This function returns the DictionaryReader object itself so
        its methods become available for use with context managers
        ('with' statements)."""
        return self

    def __exit__(self, type, value, tb):
        """ This function closes the spss data file and does some cleaning."""
        if type is not None:
            pass  # Exception occurred
        self.close()

    def close(self):
        """This function closes the spss data file and does some cleaning."""
        if not segfaults:
            self.closeSavFile(self.fh, mode="rb")

    def dataDictionary(self, asNamedtuple=False):
        """ This function returns all the dictionary items. It returns
        a Python dictionary based on the Spss dictionary of the given
        Spss file. This is equivalent to the Spss command 'DISPLAY
        DICTIONARY'. If asNamedtuple=True, one can specify things like
        metadata.valueLabels"""
        items = ["varNames", "varTypes", "valueLabels", "varLabels",
                 "formats", "missingValues", "measureLevels",
                 "columnWidths", "alignments", "varSets", "varRoles",
                 "varAttributes", "fileAttributes", "fileLabel",
                 "multRespDefs", "caseWeightVar"] # "dateVariables"]
        if self.ioUtf8:
            items = map(unicode, items)
        metadata = dict([(item, getattr(self, item)) for item in items])
        if asNamedtuple:
            Meta = collections.namedtuple("Meta", " ".join(metadata.keys()))
            return Meta(*metadata.values())
        return metadata

    def reportSpssDataDictionary(self, dataDict):
        """ This function reports information from the Spss dictionary
        of the active Spss dataset. The parameter 'dataDict' is the return
        value of dataDictionary()"""
        report = []
        #import pprint
        #pprint.pprint(dataDict)
        for kwd, allValues in sorted(dataDict.items()):
            report.append("#" + kwd.upper())
            if hasattr(allValues, "items"):
                for varName, values in allValues.iteritems():
                    if hasattr(values, "items"):
                        isList = kwd in ("missingValues", "multRespDefs")
                        for k, v in sorted(values.iteritems()):
                            if isList and isinstance(v, (list, tuple)):
                                vStr = [unicode(item).lower() for item in v]
                                report.append("%s: %s -- %s" %
                                              (varName, k, ", ".join(vStr)))
                            else:
                                report.append("%s: %s -- %s" %
                                              (varName, unicode(k).strip(), v))
                    else:
                        if isinstance(values, list):
                            entry = "%s -- %s" % (varName, ", ".join(values))
                            report.append(entry)
                        elif values != "":
                            report.append("%s -- %s" % (varName, values))
            else:
                if isinstance(allValues, basestring) and allValues:
                    allValues = [allValues]
                for varName in allValues:
                    report.append(varName)
        print(os.linesep.join(report))
        return os.linesep.join(report)
