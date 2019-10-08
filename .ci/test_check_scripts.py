import os

import pytest
from pytest import raises
from testfixtures import tempdir, compare
import yaml


from check_sripts import analyse_files

def read_fixture(expected):
    with open(os.path.join(os.path.dirname(__file__),
                           'fixtures_dir.yaml')) as fixture_file:
        fixtures = yaml.load(fixture_file, Loader=yaml.FullLoader)
    return fixtures[expected]

def create_files(tree):
    """
    Creates a list of filenames from a nested dictionary

    Parameters
    ----------
    tree: dict
      a dictionrary with nested dictionaries for each directory and
      subdirectory. When reaching a file (i.e., something.ext) the
      values must be a list with the content of the file.
    """
    output = {}
    for fname, fcontent in tree.items():
        if ".md" in fname:
            output[fname] = "\n".join(fcontent)
        else:
            midoutput = create_files(tree[fname])
            output.update({f'{fname}/{iname}': icont  for iname, icont in midoutput.items()})
    return output

@pytest.mark.parametrize("fixture", read_fixture("tree"))
def test_crate_files(fixture):
    assert fixture["expected"] == create_files(fixture["toconvert"])

@pytest.mark.parametrize("fixture", read_fixture("working"))
@tempdir()
def test_analyse(dir, fixture):
    for fname, fcontent in create_files(fixture).items():
        dir.write(fname, fcontent.encode())
    assert analyse_files(dir.path) is None

@pytest.mark.parametrize("fixture", read_fixture("failing"))
@tempdir()
def test_analyse_broken(dir, fixture):
    for fname, fcontent in create_files(fixture).items():
        dir.write(fname, fcontent.encode())
    with raises(ValueError, match=r"Some files are not linked properly:.*"):
        analyse_files(dir.path)

# TODO test that there are not extra links?
