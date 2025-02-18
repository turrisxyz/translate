#
# Copyright 2002-2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Convert XLIFF localization files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/xliff2po.html
for examples and usage instructions.
"""

from translate.storage import po, xliff


class xliff2po:
    @staticmethod
    def converttransunit(transunit):
        """makes a pounit from the given transunit"""
        thepo = po.pounit()

        # Header
        if transunit.getrestype() == "x-gettext-domain-header":
            thepo.source = ""
        else:
            thepo.source = transunit.source
        thepo.target = transunit.target

        # Location comments
        locations = transunit.getlocations()
        if locations:
            thepo.addlocations(locations)

        # NOTE: Supporting both <context> and <note> tags in xliff files
        # for comments
        # Translator comments
        trancomments = transunit.getnotes("translator")
        if trancomments:
            thepo.addnote(trancomments, origin="translator")

        # Automatic and Developer comments
        autocomments = transunit.getnotes("developer")
        if autocomments:
            thepo.addnote(autocomments, origin="developer")

        # See 5.6.1 of the spec. We should not check fuzzyness, but approved
        # attribute
        if transunit.isfuzzy():
            thepo.markfuzzy(True)

        return thepo

    def convertstore(self, inputfile, duplicatestyle="msgctxt"):
        """Converts a .xliff file to .po format"""
        XliffFile = xliff.xlifffile.parsestring(inputfile)
        thetargetfile = po.pofile()
        targetheader = thetargetfile.header()
        # TODO: support multiple files
        for transunit in XliffFile.units:
            if transunit.isheader():
                thetargetfile.updateheader(add=True, **XliffFile.parseheader())
                if transunit.getnotes("translator"):
                    targetheader.addnote(
                        transunit.getnotes("translator"),
                        origin="translator",
                        position="replace",
                    )
                if transunit.getnotes("developer"):
                    targetheader.addnote(
                        transunit.getnotes("developer"),
                        origin="developer",
                        position="replace",
                    )
                targetheader.markfuzzy(transunit.isfuzzy())
                continue
            thepo = self.converttransunit(transunit)
            thetargetfile.addunit(thepo)
        thetargetfile.removeduplicates(duplicatestyle)
        return thetargetfile


def convertxliff(inputfile, outputfile, templates, duplicatestyle="msgctxt"):
    """reads in stdin using fromfileclass, converts using convertorclass,
    writes to stdout
    """
    convertor = xliff2po()
    outputstore = convertor.convertstore(inputfile, duplicatestyle)
    if outputstore.isempty():
        return 0
    outputstore.serialize(outputfile)
    return 1


def main(argv=None):
    from translate.convert import convert

    formats = {
        "xlf": ("po", convertxliff),
        "xliff": ("po", convertxliff),
    }
    parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.run(argv)
