#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Library to extract Exif information from digital camera image files.
# https://github.com/ianare/exif-py
#
#
# VERSION 1.2.0
#
# To use this library call with:
#    f = open(path_name, 'rb')
#    tags = EXIF.process_file(f)
#
# To ignore MakerNote tags, pass the -q or --quick
# command line arguments, or as
#    tags = EXIF.process_file(f, details=False)
#
# To stop processing after a certain tag is retrieved,
# pass the -t TAG or --stop-tag TAG argument, or as
#    tags = EXIF.process_file(f, stop_tag='TAG')
#
# where TAG is a valid tag name, ex 'DateTimeOriginal'
#
# These two are useful when you are retrieving a large list of images
#
# To return an error on invalid tags,
# pass the -s or --strict argument, or as
#    tags = EXIF.process_file(f, strict=True)
#
# Otherwise these tags will be ignored
#
# Returned tags will be a dictionary mapping names of Exif tags to their
# values in the file named by path_name.  You can process the tags
# as you wish.  In particular, you can iterate through all the tags with:
#     for tag in tags.keys():
#         if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename',
#                        'EXIF MakerNote'):
#             print "Key: %s, value %s" % (tag, tags[tag])
# (This code uses the if statement to avoid printing out a few of the
# tags that tend to be long or boring.)
#
# The tags dictionary will include keys for all of the usual Exif
# tags, and will also include keys for Makernotes used by some
# cameras, for which we have a good specification.
#
# Note that the dictionary keys are the IFD name followed by the
# tag name. For example:
# 'EXIF DateTimeOriginal', 'Image Orientation', 'MakerNote FocusMode'
#
# Copyright (c) 2002-2007 Gene Cash
# Copyright (c) 2007-2013 Ianaré Sévi and contributors
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the authors nor the names of its contributors
#     may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# ----- See 'changes.txt' file for all contributors and changes ----- #
#
import sys
import getopt
import argparse

from tags import FIELD_TYPES, EXIF_TAGS, INTR_TAGS, GPS_TAGS, IGNORE_TAGS
from makernotes import MAKERNOTE_CANON_TAG_0x001, MAKERNOTE_CANON_TAG_0x004, MAKERNOTE_CANON_TAGS, \
    MAKERNOTE_CASIO_TAGS, MAKERNOTE_FUJIFILM_TAGS, MAKERNOTE_NIKON_NEWER_TAGS, MAKERNOTE_NIKON_OLDER_TAGS, \
    MAKERNOTE_OLYMPUS_TAG_0x2020, MAKERNOTE_OLYMPUS_TAGS
    
DEFAULT_STOP_TAG = "UNDEF"



def s2n_motorola(str):
    """extract multibyte integer in Motorola format (little endian)"""
    x = 0
    for c in str:
        x = (x << 8) | ord(c)
    return x

    
def s2n_intel(str):
    """extract multibyte integer in Intel format (big endian)"""
    x = 0
    y = 0
    for c in str:
        x = x | (ord(c) << y)
        y = y + 8
    return x

def gcd(a, b):
    """ratio object that eventually will be able to reduce itself to lowest
       common denominator for printing"""
    if b == 0:
        return a
    else:
        return gcd(b, a % b)

class Ratio:
    def __init__(self, num, den):
        self.num = num
        self.den = den

    def __repr__(self):
        self.reduce()
        if self.den == 1:
            return str(self.num)
        return '%d/%d' % (self.num, self.den)

    def reduce(self):
        div = gcd(self.num, self.den)
        if div > 1:
            self.num = self.num / div
            self.den = self.den / div

# for ease of dealing with tags
class IFD_Tag:
    def __init__(self, printable, tag, field_type, values, field_offset,
                 field_length):
        # printable version of data
        self.printable = printable
        # tag ID number
        self.tag = tag
        # field type as index into FIELD_TYPES
        self.field_type = field_type
        # offset of start of field in bytes from beginning of IFD
        self.field_offset = field_offset
        # length of data field in bytes
        self.field_length = field_length
        # either a string or array of data items
        self.values = values

    def __str__(self):
        return self.printable

    def __repr__(self):
        try:
            s= '(0x%04X) %s=%s @ %d' % (self.tag,
                                        FIELD_TYPES[self.field_type][2],
                                        self.printable,
                                        self.field_offset)
        except:
            s= '(%s) %s=%s @ %s' % (str(self.tag),
                                        FIELD_TYPES[self.field_type][2],
                                        self.printable,
                                        str(self.field_offset))
        return s

# class that handles an EXIF header
class EXIF_header:
    def __init__(self, file, endian, offset, fake_exif, strict, debug=0):
        self.file = file
        self.endian = endian
        self.offset = offset
        self.fake_exif = fake_exif
        self.strict = strict
        self.debug = debug
        self.tags = {}

    # convert slice to integer, based on sign and endian flags
    # usually this offset is assumed to be relative to the beginning of the
    # start of the EXIF information.  For some cameras that use relative tags,
    # this offset may be relative to some other starting point.
    def s2n(self, offset, length, signed=0):
        self.file.seek(self.offset+offset)
        slice=self.file.read(length)
        if self.endian == 'I':
            val=s2n_intel(slice)
        else:
            val=s2n_motorola(slice)
        # Sign extension ?
        if signed:
            msb=1 << (8*length-1)
            if val & msb:
                val=val-(msb << 1)
        return val

    # convert offset to string
    def n2s(self, offset, length):
        s = ''
        for dummy in range(length):
            if self.endian == 'I':
                s = s + chr(offset & 0xFF)
            else:
                s = chr(offset & 0xFF) + s
            offset = offset >> 8
        return s

    # return first IFD
    def first_IFD(self):
        return self.s2n(4, 4)

    # return pointer to next IFD
    def next_IFD(self, ifd):
        entries=self.s2n(ifd, 2)
        next_ifd = self.s2n(ifd+2+12*entries, 4)
        if next_ifd == ifd:
            return 0
        else:
            return next_ifd

    # return list of IFDs in header
    def list_IFDs(self):
        i=self.first_IFD()
        a=[]
        while i:
            a.append(i)
            i=self.next_IFD(i)
        return a

    # return list of entries in this IFD
    def dump_IFD(self, ifd, ifd_name, dict=EXIF_TAGS, relative=0, stop_tag=DEFAULT_STOP_TAG):
        entries=self.s2n(ifd, 2)
        for i in range(entries):
            # entry is index of start of this IFD in the file
            entry = ifd + 2 + 12 * i
            tag = self.s2n(entry, 2)

            # get tag name early to avoid errors, help debug
            tag_entry = dict.get(tag)
            if tag_entry:
                tag_name = tag_entry[0]
            else:
                tag_name = 'Tag 0x%04X' % tag

            # ignore certain tags for faster processing
            if not (not detailed and tag in IGNORE_TAGS):
                field_type = self.s2n(entry + 2, 2)
                
                # unknown field type
                if not 0 < field_type < len(FIELD_TYPES):
                    if not self.strict:
                        continue
                    else:
                        raise ValueError('unknown type %d in tag 0x%04X' % (field_type, tag))

                typelen = FIELD_TYPES[field_type][0]
                count = self.s2n(entry + 4, 4)
                # Adjust for tag id/type/count (2+2+4 bytes)
                # Now we point at either the data or the 2nd level offset
                offset = entry + 8

                # If the value fits in 4 bytes, it is inlined, else we
                # need to jump ahead again.
                if count * typelen > 4:
                    # offset is not the value; it's a pointer to the value
                    # if relative we set things up so s2n will seek to the right
                    # place when it adds self.offset.  Note that this 'relative'
                    # is for the Nikon type 3 makernote.  Other cameras may use
                    # other relative offsets, which would have to be computed here
                    # slightly differently.
                    if relative:
                        tmp_offset = self.s2n(offset, 4)
                        offset = tmp_offset + ifd - 8
                        if self.fake_exif:
                            offset = offset + 18
                    else:
                        offset = self.s2n(offset, 4)

                field_offset = offset
                if field_type == 2:
                    # special case: null-terminated ASCII string
                    # XXX investigate
                    # sometimes gets too big to fit in int value
                    if count != 0: # and count < (2**31):  # 2E31 is hardware dependant. --gd
                        try:
                            self.file.seek(self.offset + offset)
                            values = self.file.read(count)
                            #print values
                            # Drop any garbage after a null.
                            values = values.split('\x00', 1)[0]
                        except OverflowError:
                            values = ''
                else:
                    values = []
                    signed = (field_type in [6, 8, 9, 10])
                    
                    # XXX investigate
                    # some entries get too big to handle could be malformed
                    # file or problem with self.s2n
                    if count < 1000:
                        for dummy in range(count):
                            if field_type in (5, 10):
                                # a ratio
                                value = Ratio(self.s2n(offset, 4, signed),
                                              self.s2n(offset + 4, 4, signed))
                            else:
                                value = self.s2n(offset, typelen, signed)
                            values.append(value)
                            offset = offset + typelen
                    # The test above causes problems with tags that are 
                    # supposed to have long values!  Fix up one important case.
                    elif tag_name == 'MakerNote' :
                        for dummy in range(count):
                            value = self.s2n(offset, typelen, signed)
                            values.append(value)
                            offset = offset + typelen
                    #else :
                    #    print "Warning: dropping large tag:", tag, tag_name
                
                # now 'values' is either a string or an array
                if count == 1 and field_type != 2:
                    printable=str(values[0])
                elif count > 50 and len(values) > 20 :
                    printable=str( values[0:20] )[0:-1] + ", ... ]"
                else:
                    printable=str(values)

                # compute printable version of values
                if tag_entry:
                    if len(tag_entry) != 1:
                        # optional 2nd tag element is present
                        if callable(tag_entry[1]):
                            # call mapping function
                            printable = tag_entry[1](values)
                        else:
                            printable = ''
                            for i in values:
                                # use lookup table for this tag
                                printable += tag_entry[1].get(i, repr(i))

                self.tags[ifd_name + ' ' + tag_name] = IFD_Tag(printable, tag,
                                                          field_type,
                                                          values, field_offset,
                                                          count * typelen)
                if self.debug:
                    print(' debug:   %s: %s' % (tag_name,
                                                repr(self.tags[ifd_name + ' ' + tag_name])))
            if tag_name == stop_tag: 
                break

    # extract uncompressed TIFF thumbnail (like pulling teeth)
    # we take advantage of the pre-existing layout in the thumbnail IFD as
    # much as possible
    def extract_TIFF_thumbnail(self, thumb_ifd):
        entries = self.s2n(thumb_ifd, 2)
        # this is header plus offset to IFD ...
        if self.endian == 'M':
            tiff = 'MM\x00*\x00\x00\x00\x08'
        else:
            tiff = 'II*\x00\x08\x00\x00\x00'
        # ... plus thumbnail IFD data plus a null "next IFD" pointer
        self.file.seek(self.offset+thumb_ifd)
        tiff += self.file.read(entries*12+2)+'\x00\x00\x00\x00'

        # fix up large value offset pointers into data area
        for i in range(entries):
            entry = thumb_ifd + 2 + 12 * i
            tag = self.s2n(entry, 2)
            field_type = self.s2n(entry+2, 2)
            typelen = FIELD_TYPES[field_type][0]
            count = self.s2n(entry+4, 4)
            oldoff = self.s2n(entry+8, 4)
            # start of the 4-byte pointer area in entry
            ptr = i * 12 + 18
            # remember strip offsets location
            if tag == 0x0111:
                strip_off = ptr
                strip_len = count * typelen
            # is it in the data area?
            if count * typelen > 4:
                # update offset pointer (nasty "strings are immutable" crap)
                # should be able to say "tiff[ptr:ptr+4]=newoff"
                newoff = len(tiff)
                tiff = tiff[:ptr] + self.n2s(newoff, 4) + tiff[ptr+4:]
                # remember strip offsets location
                if tag == 0x0111:
                    strip_off = newoff
                    strip_len = 4
                # get original data and store it
                self.file.seek(self.offset + oldoff)
                tiff += self.file.read(count * typelen)

        # add pixel strips and update strip offset info
        old_offsets = self.tags['Thumbnail StripOffsets'].values
        old_counts = self.tags['Thumbnail StripByteCounts'].values
        for i in range(len(old_offsets)):
            # update offset pointer (more nasty "strings are immutable" crap)
            offset = self.n2s(len(tiff), strip_len)
            tiff = tiff[:strip_off] + offset + tiff[strip_off + strip_len:]
            strip_off += strip_len
            # add pixel strip to end
            self.file.seek(self.offset + old_offsets[i])
            tiff += self.file.read(old_counts[i])

        self.tags['TIFFThumbnail'] = tiff

    # decode all the camera-specific MakerNote formats

    # Note is the data that comprises this MakerNote.  The MakerNote will
    # likely have pointers in it that point to other parts of the file.  We'll
    # use self.offset as the starting point for most of those pointers, since
    # they are relative to the beginning of the file.
    #
    # If the MakerNote is in a newer format, it may use relative addressing
    # within the MakerNote.  In that case we'll use relative addresses for the
    # pointers.
    #
    # As an aside: it's not just to be annoying that the manufacturers use
    # relative offsets.  It's so that if the makernote has to be moved by the
    # picture software all of the offsets don't have to be adjusted.  Overall,
    # this is probably the right strategy for makernotes, though the spec is
    # ambiguous.  (The spec does not appear to imagine that makernotes would
    # follow EXIF format internally.  Once they did, it's ambiguous whether
    # the offsets should be from the header at the start of all the EXIF info,
    # or from the header at the start of the makernote.)
    def decode_maker_note(self):
        note = self.tags['EXIF MakerNote']
        
        # Some apps use MakerNote tags but do not use a format for which we
        # have a description, so just do a raw dump for these.
        #if self.tags.has_key('Image Make'):
        make = self.tags['Image Make'].printable
        #else:
        #    make = ''

        # model = self.tags['Image Model'].printable # unused

        # Nikon
        # The maker note usually starts with the word Nikon, followed by the
        # type of the makernote (1 or 2, as a short).  If the word Nikon is
        # not at the start of the makernote, it's probably type 2, since some
        # cameras work that way.
        if 'NIKON' in make:
            if note.values[0:7] == [78, 105, 107, 111, 110, 0, 1]:
                if self.debug:
                    print("Looks like a type 1 Nikon MakerNote.")
                self.dump_IFD(note.field_offset+8, 'MakerNote',
                              dict=MAKERNOTE_NIKON_OLDER_TAGS)
            elif note.values[0:7] == [78, 105, 107, 111, 110, 0, 2]:
                if self.debug:
                    print("Looks like a labeled type 2 Nikon MakerNote")
                if note.values[12:14] != [0, 42] and note.values[12:14] != [42, 0]:
                    raise ValueError("Missing marker tag '42' in MakerNote.")
                # skip the Makernote label and the TIFF header
                self.dump_IFD(note.field_offset+10+8, 'MakerNote',
                              dict=MAKERNOTE_NIKON_NEWER_TAGS, relative=1)
            else:
                # E99x or D1
                if self.debug:
                    print("Looks like an unlabeled type 2 Nikon MakerNote")
                self.dump_IFD(note.field_offset, 'MakerNote',
                              dict=MAKERNOTE_NIKON_NEWER_TAGS)
            return

        # Olympus
        if make.startswith('OLYMPUS'):
            self.dump_IFD(note.field_offset+8, 'MakerNote',
                          dict=MAKERNOTE_OLYMPUS_TAGS)
            # XXX TODO
            #for i in (('MakerNote Tag 0x2020', MAKERNOTE_OLYMPUS_TAG_0x2020),):
            #    self.decode_olympus_tag(self.tags[i[0]].values, i[1])
            #return

        # Casio
        if 'CASIO' in make or 'Casio' in make:
            self.dump_IFD(note.field_offset, 'MakerNote',
                          dict=MAKERNOTE_CASIO_TAGS)
            return

        # Fujifilm
        if make == 'FUJIFILM':
            # bug: everything else is "Motorola" endian, but the MakerNote
            # is "Intel" endian
            endian = self.endian
            self.endian = 'I'
            # bug: IFD offsets are from beginning of MakerNote, not
            # beginning of file header
            offset = self.offset
            self.offset += note.field_offset
            # process note with bogus values (note is actually at offset 12)
            self.dump_IFD(12, 'MakerNote', dict=MAKERNOTE_FUJIFILM_TAGS)
            # reset to correct values
            self.endian = endian
            self.offset = offset
            return

        # Canon
        if make == 'Canon':
            self.dump_IFD(note.field_offset, 'MakerNote',
                          dict=MAKERNOTE_CANON_TAGS)
            for i in (('MakerNote Tag 0x0001', MAKERNOTE_CANON_TAG_0x001),
                      ('MakerNote Tag 0x0004', MAKERNOTE_CANON_TAG_0x004)):
                if i[0] in self.tags:
                   self.canon_decode_tag(self.tags[i[0]].values, i[1])
            return


    # XXX TODO decode Olympus MakerNote tag based on offset within tag
    def olympus_decode_tag(self, value, dict):
        pass

    # decode Canon MakerNote tag based on offset within tag
    # see http://www.burren.cx/david/canon.html by David Burren
    def canon_decode_tag(self, value, dict):
        for i in range(1, len(value)):
            x=dict.get(i, ('Unknown', ))
            if self.debug:
                print(i, x)
            name=x[0]
            if len(x) > 1:
                val=x[1].get(value[i], 'Unknown')
            else:
                val=value[i]
            # it's not a real IFD Tag but we fake one to make everybody
            # happy. this will have a "proprietary" type
            self.tags['MakerNote '+name]=IFD_Tag(str(val), None, 0, None,
                                                 None, None)

# process an image file (expects an open file object)
# this is the function that has to deal with all the arbitrary nasty bits
# of the EXIF standard
def process_file(f, stop_tag=DEFAULT_STOP_TAG, details=True, strict=False, debug=False):
    # yah it's cheesy...
    global detailed
    detailed = details

    # by default do not fake an EXIF beginning
    fake_exif = 0

    # determine whether it's a JPEG or TIFF
    data = f.read(12)
    if data[0:4] in ['II*\x00', 'MM\x00*']:
        # it's a TIFF file
        f.seek(0)
        endian = f.read(1)
        f.read(1)
        offset = 0
    elif data[0:2] == '\xFF\xD8':
        # it's a JPEG file
        if debug: print("JPEG format recognized data[0:2] == '0xFFD8'.")
        base = 2
        while data[2] == '\xFF' and data[6:10] in ('JFIF', 'JFXX', 'OLYM', 'Phot'):
            if debug: print("data[2] == 0xxFF data[3]==%x and data[6:10] = %s"%(ord(data[3]),data[6:10]))
            length = ord(data[4])*256+ord(data[5])
            if debug: print("Length offset is",length)
            f.read(length-8)
            # fake an EXIF beginning of file
            # I don't think this is used. --gd
            data = '\xFF\x00'+f.read(10)
            fake_exif = 1
            if base>2: 
                if debug: print("added to base ")
                base = base + length + 4 -2
            else: 
                if debug: print("added to zero ")
                base = length + 4
            if debug: print("Set segment base to",base)

        # Big ugly patch to deal with APP2 (or other) data coming before APP1
        f.seek(0)
        data = f.read(base+4000) # in theory, this could be insufficient since 64K is the maximum size--gd
        # base = 2
        while 1:
            if debug: print("Segment base 0x%X" % base)
            if data[base:base+2]=='\xFF\xE1':
                # APP1
                if debug: print("APP1 at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if data[base+4:base+8] == "Exif":
                    if debug: print("Decrement base by",2,"to get to pre-segment header (for compatibility with later code)")
                    base = base-2
                    break
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xE0':
                # APP0
                if debug: print("APP0 at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xE2':
                # APP2
                if debug: print("APP2 at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xEE':
                # APP14
                if debug: print("APP14 Adobe segment at base",hex(base))
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                print("There is useful EXIF-like data here, but we have no parser for it.")
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xDB':
                if debug: print("JPEG image data at base",hex(base),"No more segments are expected.")
                # sys.exit(0)
                break
            elif data[base:base+2]=='\xFF\xD8':
                # APP12
                if debug: print("FFD8 segment at base",hex(base))
                if debug: print("Got",hex(ord(data[base])), hex(ord(data[base+1])),"and", data[4+base:10+base], "instead.")
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            elif data[base:base+2]=='\xFF\xEC':
                # APP12
                if debug: print("APP12 XMP (Ducky) or Pictureinfo segment at base",hex(base))
                if debug: print("Got",hex(ord(data[base])), hex(ord(data[base+1])),"and", data[4+base:10+base], "instead.")
                if debug: print("Length",hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code",data[base+4:base+8])
                if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                print("There is useful EXIF-like data here (quality, comment, copyright), but we have no parser for it.")
                base=base+ord(data[base+2])*256+ord(data[base+3])+2
            else: 
                try:
                    if debug: print("Unexpected/unhandled segment type or file content.")
                    if debug: print("Got",hex(ord(data[base])), hex(ord(data[base+1])),"and", data[4+base:10+base], "instead.")
                    if debug: print("Increment base by",ord(data[base+2])*256+ord(data[base+3])+2)
                except: pass
                try: base=base+ord(data[base+2])*256+ord(data[base+3])+2
                except: return {}
        f.seek(base+12)
        if data[2+base] == '\xFF' and data[6+base:10+base] == 'Exif':
            # detected EXIF header
            offset = f.tell()
            endian = f.read(1)
            #HACK TEST:  endian = 'M'
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Ducky':
            # detected Ducky header.
            if debug: print("EXIF-like header (normally 0xFF and code):",hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Adobe':
            # detected APP14 (Adobe)
            if debug: print("EXIF-like header (normally 0xFF and code):",hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        else:
            # no EXIF information
            if debug: print("No EXIF header expected data[2+base]==0xFF and data[6+base:10+base]===Exif (or Duck)")
            if debug: print(" but got",hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            return {}
    else:
        # file format not recognized
        if debug: print("file format not recognized")
        return {}

    # deal with the EXIF info we found
    if debug:
        print("Endian format is ",endian)
        print({'I': 'Intel', 'M': 'Motorola', '\x01':'Adobe Ducky', 'd':'XMP/Adobe unknown' }[endian], 'format')
    hdr = EXIF_header(f, endian, offset, fake_exif, strict, debug)
    ifd_list = hdr.list_IFDs()
    ctr = 0
    for i in ifd_list:
        if ctr == 0:
            IFD_name = 'Image'
        elif ctr == 1:
            IFD_name = 'Thumbnail'
            thumb_ifd = i
        else:
            IFD_name = 'IFD %d' % ctr
        if debug:
            print(' IFD %d (%s) at offset %d:' % (ctr, IFD_name, i))
        hdr.dump_IFD(i, IFD_name, stop_tag=stop_tag)
        # EXIF IFD
        exif_off = hdr.tags.get(IFD_name+' ExifOffset')
        if exif_off:
            if debug:
                print(' EXIF SubIFD at offset %d:' % exif_off.values[0])
            hdr.dump_IFD(exif_off.values[0], 'EXIF', stop_tag=stop_tag)
            # Interoperability IFD contained in EXIF IFD
            intr_off = hdr.tags.get('EXIF SubIFD InteroperabilityOffset')
            if intr_off:
                if debug:
                    print(' EXIF Interoperability SubSubIFD at offset %d:' \
                          % intr_off.values[0])
                hdr.dump_IFD(intr_off.values[0], 'EXIF Interoperability',
                             dict=INTR_TAGS, stop_tag=stop_tag)
        # GPS IFD
        gps_off = hdr.tags.get(IFD_name+' GPSInfo')
        if gps_off:
            if debug:
                print(' GPS SubIFD at offset %d:' % gps_off.values[0])
            hdr.dump_IFD(gps_off.values[0], 'GPS', dict=GPS_TAGS, stop_tag=stop_tag)
        ctr += 1

    # extract uncompressed TIFF thumbnail
    thumb = hdr.tags.get('Thumbnail Compression')
    if thumb and thumb.printable == 'Uncompressed TIFF':
        hdr.extract_TIFF_thumbnail(thumb_ifd)

    # JPEG thumbnail (thankfully the JPEG data is stored as a unit)
    thumb_off = hdr.tags.get('Thumbnail JPEGInterchangeFormat')
    if thumb_off:
        f.seek(offset+thumb_off.values[0])
        size = hdr.tags['Thumbnail JPEGInterchangeFormatLength'].values[0]
        hdr.tags['JPEGThumbnail'] = f.read(size)

    # deal with MakerNote contained in EXIF IFD
    # (Some apps use MakerNote tags but do not use a format for which we
    # have a description, do not process these).
    if 'EXIF MakerNote' in hdr.tags and 'Image Make' in hdr.tags and detailed:
        hdr.decode_maker_note()

    # Sometimes in a TIFF file, a JPEG thumbnail is hidden in the MakerNote
    # since it's not allowed in a uncompressed TIFF IFD
    if 'JPEGThumbnail' not in hdr.tags:
        thumb_off=hdr.tags.get('MakerNote JPEGThumbnail')
        if thumb_off:
            f.seek(offset+thumb_off.values[0])
            hdr.tags['JPEGThumbnail']=file.read(thumb_off.field_length)

    return hdr.tags


def main():
    parser = argparse.ArgumentParser(description='Extract EXIF information from digital camera image files.', usage='%(prog)s [OPTIONS] image1 [image2 ...]')
    parser.add_argument('images', nargs='+', help='Images to process')
    parser.add_argument('-q', '--quick', dest='detailed', action="store_false", help='Do not process MakerNotes')
    parser.add_argument('-t', '--stop-tag', dest="stop_tag", default=DEFAULT_STOP_TAG, help="Stop processing when this tag is retrieved (default is '%s')" % DEFAULT_STOP_TAG)
    parser.add_argument('-s', '--strict', action="store_true", help='Run in strict mode (stop on errors)')
    parser.add_argument('-d', '--debug', action="store_true", help='Run in debug mode (display extra info)')
    
    args = parser.parse_args()
    
    detailed = args.detailed
    stop_tag = args.stop_tag
    strict = args.strict
    debug = args.debug
    
    for filename in args.images:
        try:
            file=open(str(filename), 'rb')
        except:
            print("'%s' is unreadable\n"%filename)
            continue
        print(filename + ':')
        # get the tags
        data = process_file(file, stop_tag=stop_tag, details=detailed, strict=strict, debug=debug)
        if not data:
            print('No EXIF information found')
            continue

        x=data.keys()
        x.sort()
        for i in x:
            if i in ('JPEGThumbnail', 'TIFFThumbnail'):
                continue
            try:
                print('   %s (%s): %s' % \
                      (i, FIELD_TYPES[data[i].field_type][2], data[i].printable))
            except:
                print('error', i, '"', data[i], '"')
        if 'JPEGThumbnail' in data:
            print('File has JPEG thumbnail')
        
    
