# https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format

import os
import ntpath
import asyncio

basepath = os.path.basename(ntpath.basename(__file__))
dirpath = os.path.dirname(os.path.realpath(__file__))
file = os.path.basename(os.path.realpath(__file__))

print(f"{basepath =} {dirpath = } {file = }")



# Of course, if the file ends with a slash, the basename will be empty, so make your own function to deal with it:

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

# Verification:

async def leaf(path: os.path):
    # ['c', 'c', 'c', 'c', 'c', 'c', 'c']
    print(path_leaf(path))
    return path_leaf(path)


if __name__ == "__main__":
    # ntpath.basename("a/b/c")
    # testpaths = ['a/b/c/', 'a/b/c', '\\a\\b\\c', '\\a\\b\\c\\', 'a\\b\\c', 'a/b/../../a/b/c/', 'a/b/../../a/b/c']
    # print([path_leaf(path) for path in testpaths])
    asyncio.run(leaf(os.path.basename(__file__)))