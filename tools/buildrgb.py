#!/usr/bin/env python3
import sys


def main():
    print("from larry import Color\n\n")
    print("NAMES = {")
    rgb_txt = sys.argv[1]
    with open(rgb_txt) as rgbfile:
        for line in rgbfile:
            line = line.strip()
            if not line or line[0] == "#":
                continue
            red, green, blue, name = line.split(None, 3)
            print(f"    {name.lower()!r}: Color({red}, {green}, {blue}),")
    print("}")


if __name__ == "__main__":
    main()
