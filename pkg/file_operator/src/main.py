import builtins
import json
import os
import re
import shutil
import typing as t
import zipfile
from datetime import datetime
from pathlib import Path

import yaml


def _unsupported_type_error(x: t.Any) -> Exception:
    return TypeError(f"Unsupported type. Type:{type(x)}")


# --- file

def load_file(filepath: t.Union[str, Path], return_cls: t.Any = builtins.bytes) -> t.Any:
    """
    read file -> parse to return_cls type.
    filetype support [json, yaml, txt(json,yaml)]
    return_cls base type of python3, support builtins->[bytes, str, int, float, list, dict, tuple, set, None ]

    Args:
        filepath: file path
        return_cls: return type is the same type of return_cls

    Returns:
        return type is the same type of return_cls

        e.q. load_file('./test.json', dict)
        e.q. load_file('./test.yaml', str)
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
    elif isinstance(filepath, Path):
        ...
    else:
        raise TypeError(f"filepath type error.Type:{type(filepath)}")

    assert filepath.exists(), f"No such file ,{filepath}"
    assert type(return_cls) is type, 'return_cls should be base type of python3. e.q. int dict'

    data = None
    with open(filepath, 'rb') as f:
        data = f.read()
    assert data is not None, 'read data is empty'

    # bytes
    if return_cls is bytes:
        return data

    # other types
    default_encoding = 'utf-8'
    data = data.decode(default_encoding).strip()
    if return_cls is str:
        return data
    elif return_cls is int:
        return int(data)
    elif return_cls is float:
        return float(data)
    elif return_cls is bool:
        return bool(data)
    elif return_cls is None:
        return None
    elif return_cls is list:
        return json.loads(data)
    elif return_cls is set:
        return set(json.loads(data))
    elif return_cls is tuple:
        return tuple(json.loads(data))
    elif return_cls is dict:
        suffix = filepath.name.split(".")[-1]
        if suffix in ('json',):
            data = json.loads(data)
        elif suffix in ('yaml', 'yml'):
            data = yaml.load(data, Loader=yaml.FullLoader)
        elif suffix in ('txt',):
            data = json.loads(data) if data.startswith('{') else yaml.load(data, Loader=yaml.FullLoader)
        else:
            raise TypeError(f"Func Present not support this type file.{suffix}.Please dev func")
    else:
        raise TypeError(f"Not support return this type.type:{type(return_cls)}.Please dev func")

    return data


def find(root: t.Union[str, Path], rule: t.Union[str, re.Pattern], *, _type: str = 'file', depth: int = 1) \
        -> t.List[Path]:
    """
    find file in root
    Args:
        root: find in which dir path
        rule: match rule  str in filename of  re.Pattern Match filename
        _type: Enum[file, dir]
        depth: find dir depth limit.1 only in root. -1 no depth limit


    Returns:
        match file list[pathlib.Path]

    """
    if isinstance(root, str):
        root = Path(root)
    elif isinstance(root, Path):
        ...
    else:
        raise _unsupported_type_error(root)

    assert root.exists() and root.is_dir(), f"Root should be a str and existed.root = {root}"

    if isinstance(rule, (str, re.Pattern)):
        ...
    else:
        raise _unsupported_type_error(rule)

    # core
    _res = []
    _depth = 0
    for _root, dir_names, filenames in os.walk(root):
        if depth != -1 and _depth >= depth:
            break
        _depth += 1
        for f in filenames:
            p = Path(_root).joinpath(f)
            if _type == 'file' and \
                    (isinstance(rule, str) and rule in p.name) or \
                    (isinstance(rule, re.Pattern) and rule.match(p.name)):
                _res.append(p.absolute())
        for d in dir_names:
            p = Path(_root).joinpath(d)
            if _type == 'dir' and \
                    (isinstance(rule, str) and rule in p.name) or \
                    (isinstance(rule, re.Pattern) and rule.match(p.name)):
                _res.append(p.absolute())
            find(p, rule, _type=_type, depth=depth - 1)

    return _res


# --- dir

def del_dir(root: t.Union[str, Path], dir_name: t.Union[str, re.Pattern], safety: bool = True) -> None:
    """
    we won't delete root even then dir_name eq root

    Args:
        root: root path is the parent of dir_name
        dir_name: str for regexp or re.Pattern .del_dir the need del dir name pattern
        safety: True, only allow del one dir. False all match dir del

    Returns:
        None
    """
    if isinstance(root, str):
        root = Path(root)
    elif isinstance(root, Path):
        ...
    else:
        raise TypeError("can't support root type.type should in [str, pathlib.Path]")

    if isinstance(dir_name, str):
        dir_name = re.compile(dir_name)
    elif isinstance(dir_name, re.Pattern):
        ...
    else:
        raise TypeError("can't support dir_name. type should in [str, re.Pattern]")

    root = root.absolute()
    assert root.exists() and root.is_dir(), f'root path should exist and be a dir.{root}'
    # add path
    remove_set = set()
    for p, _, _ in os.walk(root, topdown=False):
        p: Path = Path(p)
        if p.__eq__(root):
            continue
        if p.is_dir() and dir_name.match(p.name):
            remove_set.add(str(p))

    if safety:
        assert len(remove_set) <= 1, f'safety mode only remove one dir but now :{len(remove_set)}'

    # remove
    if len(remove_set) == 1 or not safety:
        for n in remove_set:
            p = Path(n)
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
    return


def zip_dir(source_dir: t.Union[str, Path],
            zipfile_dir: t.Union[str, Path] = None,
            zip_filename: str = None,
            withtime: bool = False,
            *,
            exclude_dirs: t.List[str] = None,
            exclude_files: t.List[str] = None) -> t.Optional[Path]:
    """

    Args:
        source_dir: dir path for zip
        zipfile_dir: dir path for where zip file save (ps: should not sub dir of source_dir)
        zip_filename: zip filename
        withtime: zip filename take time (xxx_200102030405.zip)
        exclude_dirs:
        exclude_files:

    Returns:
        str (zip filepath)
        None (zip failed)
    """

    if isinstance(source_dir, (str, Path)):
        source_dir = Path(source_dir)
    else:
        raise _unsupported_type_error(source_dir)
    assert source_dir.exists() and source_dir.is_dir(), f'zip origin not exist or is not a dir,Path:{source_dir}'

    if zipfile_dir is None:
        zipfile_dir = source_dir.parent.joinpath(f'to_zip/{source_dir.name}/')
    if isinstance(zipfile_dir, (str, Path)):
        zipfile_dir = Path(zipfile_dir)
    else:
        raise _unsupported_type_error(zipfile_dir)
    assert not zipfile_dir.absolute().is_relative_to(source_dir), 'output should be sub dir of source_dir'

    assert isinstance(zip_filename, str) or zip_filename is None, \
        f'zip_filename type error,{type(zip_filename)}'
    if zip_filename is None:
        zip_filename = source_dir.name
    assert isinstance(withtime, bool), 'withtime should be bool'

    # zipfile
    zipfile_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = zip_filename.split('.')[0]
    if withtime:
        pres_time_str = datetime.now().strftime("%y%m%d_%H%M%S")
        zip_filename = f"{zip_filename + f'_{pres_time_str}'}.zip"
    else:
        zip_filename = f"{zip_filename}.zip"

    zipfile_path = zipfile_dir.joinpath(zip_filename)

    zipFIle = zipfile.ZipFile(
        zipfile_path,
        mode='w'
    )
    for root, _, files in os.walk(source_dir):
        root = Path(root)
        if exclude_dirs and any([x in str(root) for x in exclude_dirs]):
            continue
        arc_root = Path(root).relative_to(source_dir)
        zipFIle.write(root, arc_root)
        for f in files:
            if exclude_files and any([x in f for x in exclude_dirs]):
                continue
            zipFIle.write(root.joinpath(f), arc_root.joinpath(f))
    zipFIle.close()

    return zipfile_path


def size_of_dir(root: t.Union[str, Path], unit: str = 'byte') -> float:
    """
    Get size of dir
    Args:
        root: target dir
        unit: count unit . e.q. byte kb mb gb tb

    Returns:
        bytes of size.
        float and keep 2 decimal

    """
    assert isinstance(root, (str, Path)), f"Unsupported type of root . Got {type(root)}"
    unit = unit.lower()

    size = 0
    for start, _, files in os.walk(root):
        size += sum([os.path.getsize(Path(start).joinpath(filename)) for filename in files])

    unit_level = {"byte": 1, "kb": 2, 'mb': 3, "gb": 4, "tb": 5}
    pres = 1
    to_level = unit_level.get(unit, 1)  # default byte
    for _ in range(to_level - pres):
        size /= 1024
    return float(round(size, 2))
