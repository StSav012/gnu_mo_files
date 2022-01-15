# coding: utf-8
import sys
from os import PathLike
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Literal, Sequence, Union

__version__ = '0.0.1'
__all__ = ('read_mo_file', 'write_mo_file')


def read_mo_file(filename: Union[str, PathLike], encoding: str = sys.getdefaultencoding()) -> Dict[str, str]:
    filename = Path(filename)
    f_in: BinaryIO
    with filename.open('rb') as f_in:
        magic_number: int = int.from_bytes(f_in.read(4), byteorder=sys.byteorder)
        if magic_number not in (0x950412de, 0xde120495):
            raise RuntimeError('Malformed GNU MO file')
        byte_order: Literal['big', 'little']
        if magic_number == 0x950412de:
            byte_order = sys.byteorder
        elif magic_number == 0xde120495:
            if sys.byteorder == 'big':
                byte_order = 'little'
            elif sys.byteorder == 'little':
                byte_order = 'big'
            else:
                raise NotImplementedError(f'Unknown system byte order: {sys.byteorder}')
        else:
            raise RuntimeError('Malformed GNU MO file')

        int.from_bytes(f_in.read(4), byteorder=byte_order)  # file_format_revision
        number_of_strings: int = int.from_bytes(f_in.read(4), byteorder=byte_order)
        offset_of_table_with_original_strings: int = int.from_bytes(f_in.read(4), byteorder=byte_order)
        offset_of_table_with_translation_strings: int = int.from_bytes(f_in.read(4), byteorder=byte_order)
        int.from_bytes(f_in.read(4), byteorder=byte_order)  # size_of_hashing_table
        int.from_bytes(f_in.read(4), byteorder=byte_order)  # offset_of_hashing_table

        index: int

        f_in.seek(offset_of_table_with_original_strings)
        original_string_lengths: List[int] = [0] * number_of_strings
        original_string_offsets: List[int] = [0] * number_of_strings
        for index in range(number_of_strings):
            original_string_lengths[index] = int.from_bytes(f_in.read(4), byteorder=byte_order)
            original_string_offsets[index] = int.from_bytes(f_in.read(4), byteorder=byte_order)

        f_in.seek(offset_of_table_with_translation_strings)
        translation_string_lengths: List[int] = [0] * number_of_strings
        translation_string_offsets: List[int] = [0] * number_of_strings
        for index in range(number_of_strings):
            translation_string_lengths[index] = int.from_bytes(f_in.read(4), byteorder=byte_order)
            translation_string_offsets[index] = int.from_bytes(f_in.read(4), byteorder=byte_order)

        original_strings: List[str] = [''] * number_of_strings
        for index in range(number_of_strings):
            f_in.seek(original_string_offsets[index])
            original_strings[index] = f_in.read(original_string_lengths[index]).decode(encoding=encoding)

        translation_strings: List[str] = [''] * number_of_strings
        for index in range(number_of_strings):
            f_in.seek(translation_string_offsets[index])
            translation_strings[index] = f_in.read(translation_string_lengths[index]).decode(encoding=encoding)

        return dict(zip(original_strings, translation_strings))


def write_mo_file(filename: Union[str, PathLike], translations: Dict[str, str],
                  encoding: str = sys.getdefaultencoding()) -> None:
    filename = Path(filename)
    original_bytes: List[bytes] = list(map(lambda s: s.encode(encoding=encoding), translations.keys()))
    translation_bytes: List[bytes] = list(map(lambda s: s.encode(encoding=encoding), translations.values()))

    # https://stackoverflow.com/a/3382369/8554611
    def arg_sort(seq: Sequence[Any]) -> List[int]:
        # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
        return sorted(range(len(seq)), key=seq.__getitem__)

    # sort the items
    sorting_indices: List[int] = arg_sort(original_bytes)
    original_bytes = [original_bytes[i] for i in sorting_indices]
    translation_bytes = [translation_bytes[i] for i in sorting_indices]

    f_out: BinaryIO
    with filename.open('wb') as f_out:
        magic_number: int = 0x950412de
        f_out.write(magic_number.to_bytes(4, byteorder=sys.byteorder))
        file_format_revision: int = 0
        f_out.write(file_format_revision.to_bytes(4, byteorder=sys.byteorder))
        number_of_strings: int = len(translations)
        f_out.write(number_of_strings.to_bytes(4, byteorder=sys.byteorder))
        offset_of_table_with_original_strings: int = 28
        f_out.write(offset_of_table_with_original_strings.to_bytes(4, byteorder=sys.byteorder))
        offset_of_table_with_translation_strings: int = \
            offset_of_table_with_original_strings + len(original_bytes) * 8
        f_out.write(offset_of_table_with_translation_strings.to_bytes(4, byteorder=sys.byteorder))
        size_of_hashing_table: int = 0
        f_out.write(size_of_hashing_table.to_bytes(4, byteorder=sys.byteorder))
        offset_of_hashing_table: int = offset_of_table_with_translation_strings + len(translation_bytes) * 8
        f_out.write(offset_of_hashing_table.to_bytes(4, byteorder=sys.byteorder))

        original_item: bytes
        original_item_offset: int = offset_of_hashing_table + size_of_hashing_table * 4
        for original_item in original_bytes:
            original_item_length: int = len(original_item)
            f_out.write(original_item_length.to_bytes(4, byteorder=sys.byteorder))
            f_out.write(original_item_offset.to_bytes(4, byteorder=sys.byteorder))
            original_item_offset += original_item_length + 1

        translation_item: bytes
        translation_item_offset: int = original_item_offset
        for translation_item in translation_bytes:
            translation_item_length: int = len(translation_item)
            f_out.write(translation_item_length.to_bytes(4, byteorder=sys.byteorder))
            f_out.write(translation_item_offset.to_bytes(4, byteorder=sys.byteorder))
            translation_item_offset += translation_item_length + 1

        f_out.writelines(map(lambda b: b + b'\00', original_bytes))
        f_out.writelines(map(lambda b: b + b'\00', translation_bytes))


if __name__ == '__main__':
    import argparse
    import os
    from typing import TextIO

    ap: argparse.ArgumentParser = argparse.ArgumentParser(description='export a GNU MO file to a plain text file')
    ap.add_argument('--encoding', help='text file encoding', default=sys.getdefaultencoding())
    ap.add_argument('source', help='GNU MO file location')
    ap.add_argument('destination', help='file to save to; standard output if omitted', nargs='?')
    # https://stackoverflow.com/a/4042861/8554611
    if len(sys.argv) == 1:
        ap.print_help(sys.stderr)
        sys.exit(1)
    args: argparse.Namespace = ap.parse_args()


    def to_plain_text(file: TextIO, translations: Dict[str, str]) -> None:
        def escape(text: str, characters: str) -> str:
            lines: List[str] = text.splitlines(keepends=True)
            index: int
            for index in range(len(lines)):
                if lines[index].startswith(characters):
                    lines[index] = '\\' + lines[index]
            return ''.join(lines)

        key: str
        value: str
        for key, value in translations.items():
            key = escape(key, '<')
            value = escape(value, '>')
            file.write('>' + key + os.linesep)
            file.write('<' + value + os.linesep)


    if args.destination is not None:
        f_out: TextIO
        with open(args.destination, 'wt', encoding=args.encoding) as f_out:
            to_plain_text(f_out, read_mo_file(args.source, encoding=args.encoding))
    else:
        to_plain_text(sys.stdout, read_mo_file(args.source, encoding=args.encoding))
