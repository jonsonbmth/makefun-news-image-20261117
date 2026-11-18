#!/usr/bin/env python3
"""Entry program for the make.fun bounty 'Sum up 17 November's world news
in one image' (news-image-20261117).

Copies the pre-built front page (entry.png) from this repository into the
output directory. The image is JPEG bytes in a file named entry.png, which
the competition rules allow (PNG or JPEG, told apart by first bytes).

Standard library only. Runs offline. Deterministic: every run writes the
exact same bytes, so two runs are byte-identical.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main():
    if not os.path.isfile(SOURCE):
        raise SystemExit("missing source image: %s" % SOURCE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    print("wrote %s (%d bytes)" % (dest, os.path.getsize(dest)))


if __name__ == "__main__":
    main()
