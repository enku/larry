#!/usr/bin/env python3
"""build rgb.py based on rgb.txt

Usage: python buildrgb.py /path/to/rgb.txt
"""
import sys


def main():
    """Entry point"""
    print("from larry.color import Color\n\n")
    print("NAMES = {")
    rgb_txt = sys.argv[1]
    with open(rgb_txt, encoding="utf8") as rgbfile:
        for line in rgbfile:
            line = line.strip()
            if not line or line[0] == "#":
                continue
            red, green, blue, name = line.split(None, 3)
            print(f"    {name.lower()!r}: Color({red}, {green}, {blue}),")
    print("}")


if __name__ == "__main__":
    main()
