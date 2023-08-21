from pathlib import Path
import zipfile
from exifread import process_file

BIG_TIFF_PACKAGE: str = "compressed_asset.large.zip"
TIFF_PACKAGE: str = "compressed_asset.zip"
PARENT_PATH: str = "/Users/jose.delgado/delivery_data"
path = zipfile.Path(Path(PARENT_PATH).joinpath(BIG_TIFF_PACKAGE))

for file_name in path.root.namelist():
    if ".tif" not in file_name.lower():
        continue
    path.at = file_name
    with path.open("rb") as fo:
        header = process_file(fo)
    break
for key, value in header.items():
    if value.tag == 34737:
        print(value.values)
# print(header)

"""
Struggling with the following byte string: b'E\x00\x00\x7fC\xb0\xd4\x00'

- `E` is a shift-out character with no practical use https://en.wikipedia.org/wiki/Shift_Out_and_Shift_In_characters
- `\x7f` is a delete charater https://en.wikipedia.org/wiki/Delete_character
- `C` is form feed, or page break https://en.wikipedia.org/wiki/Page_break
- `\x00` is NULL and every ASCII string should end in a NULL

So the byte string should break into something like:
b'\x00\x00'
b'\xb0\xd4\x00'

Also from the tiff specification:

Note on ASCII Keys:

Special handling is required for
ASCII-valued keys. While it is true that
TIFF 6.0 permits multiple NULL-delimited
strings within a single ASCII tag, the secondary
strings might not appear in the output of naive "tiffdump"
programs. For this reason, the null delimiter of each 
ASCII Key value shall be converted to 
a "|" (pipe) character before being 
installed back into the ASCII holding 
tag, so that a dump of the tag will look like this.

"|" is b'\x7c' in hex

values.replace(b'b'\x7c',)

   AsciiTag="first_value|second_value|etc...last_value|"

"""