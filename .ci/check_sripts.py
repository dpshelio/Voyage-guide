import glob
import json
import os

import markdown_link_extractor


def linked_from_parent(filename, path):
    """
    Returns True if the parent directory has a README.md linking to the input file.
    """
    dirs = filename.split('/')

    # Browse through subdirectories
    if len(dirs) > 1:
        # Are we on an 'index' (readme) page or in a place page?
        if dirs[-1].lower() == "readme.md":
            n = -2 # check for the directory above.
        else:
            n = -1 # check for the readme in this directory.
        # All parents pages need to be README.md
        parent = os.path.join(*dirs[:n], 'README.md')

        try:
            with open(path + parent) as ff:
                content = ff.read()
            links = markdown_link_extractor.getlinks(content)
            # Review all the links of the parent - return when one matches.
            for link in links:
                dest = link.split('/')
                if len(dest) > 1 and dest[-2] != '.':
                    n = -2
                else:
                    n = -1
                # compare only what's needed depending how the link was created
                if dest[n:] == dirs[n:]:
                    return True
        except FileNotFoundError:
            return False # as it is not linked and it shouldn't be.
    elif len(dirs) == 1 and dirs[0] == "README.md":
        return True # Uppermost README.md
    return False

def wiki_link(filename, path):
    """
    Returns True if the place page contains a link to a wiki place.
    """
    if 'README.md' in filename:
        return True # Indices don't need the wiki link.

    with open(path + filename) as ff:
        content = ff.read()
    links = markdown_link_extractor.getlinks(content)
    for link in links:
        if link.startswith('http') and 'wiki' in link:
            return True
    return False

def analyse_files(path="./"):
    """
    Run over all the markdown files and find which ones are not linked
    from the above pages.
    """
    # Get all the directories
    if path[-1] != '/':
        path = path + '/'
    mdfiles = sorted(glob.glob(path + '**/*.md', recursive=True), reverse=True)
    mdfiles = [n for n in mdfiles if 'test' not in n]

    structure = {}
    for mdfile in mdfiles:
        mdfile = mdfile.replace(path, '')
        structure[mdfile] = {'link_parent': linked_from_parent(mdfile, path),
                             'external_link': wiki_link(mdfile, path)}

    errors = {'link_parent':[], 'external_link':[]}
    any_error = list()
    for key, val in structure.items():
        for error_missing in val.keys():
            if not val[error_missing]:
                errors[error_missing].append(key)
                any_error.append(key)

    if any_error:
        raise ValueError("Some files are not linked properly:\nmissing:\n" +
                         json.dumps(errors, indent=4))

if __name__ == "__main__":
    analyse_files()
