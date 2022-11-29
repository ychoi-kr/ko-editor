#!/usr/bin/python3

import argparse

import fileutil


def insert_fig_num(new_fig_num, dry_run):
    fileutil.rename_numbered_files(new_fig_num, True, dry_run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("new_fig_num")
    parser.add_argument('--dry_run', action="store_true")
    args = parser.parse_args()
    insert_fig_num(args.new_fig_num, args.dry_run)
