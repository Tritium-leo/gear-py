import copy
import json
import re
import shutil
import tarfile
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from PIL import Image, ImageDraw


def filepath_validater(filepath: t.Any) -> Path:
    if not isinstance(filepath, (str, Path)):
        raise TypeError("filepath should be str or Path")
    filepath = Path(filepath)
    return filepath


class Faker(ABC):
    @abstractmethod
    def fake(self, *args, **kwargs):
        """ main func of faker"""
        raise NotImplementedError


class FileFaker(Faker):
    _update_img: bool = True

    @classmethod
    def image_extension(cls) -> dict:
        if cls._update_img:
            pres = copy.deepcopy(Image.EXTENSION)
            Image.init()
            update = copy.deepcopy(Image.EXTENSION)
            if pres == update:
                cls._update_img = False
        return copy.deepcopy(Image.EXTENSION)

    @staticmethod
    def _fake_wav_file(filepath: t.Union[str, Path], content: t.Any = None,
                       voice_dir: t.Union[str, Path] = None) -> Path:
        from pydub import AudioSegment
        from xpinyin import Pinyin

        filepath = filepath_validater(filepath)

        voice_dir = '../data/voice' if voice_dir is None else voice_dir
        voice_dir = filepath_validater(voice_dir)
        assert voice_dir.exists(), f"voice_dir didn't exist.value :{voice_dir}"

        if isinstance(content, AudioSegment):
            ...
        elif isinstance(content, str) or content is None:
            # str or None
            origin = '夕阳西下' if content is None else content
            # to pinyin file
            p = Pinyin()
            punc = '~`!#$%^&amp;*()_+-=|\';":/.,?&gt;&lt;~·！@#￥%……&amp;*（）——+-=“：’；、。，？》《{} \n'
            wenzi_data = re.sub(r"[%s]+" % punc, "0", origin)
            ret = p.get_pinyin(wenzi_data, tone_marks='numbers')
            voi = ret.split('-')
            # process
            sounds = []
            playlist = AudioSegment.empty()
            for i in voi:
                i = i.lower()
                voice_filepath = voice_dir.joinpath(f"{i}.wav")
                try:
                    data = AudioSegment.from_wav(voice_filepath)
                    sounds.append(data)
                except Exception:
                    sounds.append(AudioSegment.silent(duration=230, frame_rate=1600))  # replace by empty
                    print(f"Require Voice File: {voice_filepath}")
            for sound in sounds:
                playlist += sound + 15  # voice + 15

            content = playlist
        else:
            raise TypeError(f"unsupported type of content: {type(content)} , value:{content}")

        content.export(filepath, format='wav')

        return filepath

    @staticmethod
    def _fake_txt_file(filepath: t.Union[str, Path], content: t.Any = None) -> Path:
        filepath = filepath_validater(filepath)

        content = 'fake txt content' if content is None else content

        import pickle
        pk = pickle.dumps(content)
        with open(filepath, 'wb') as f:
            f.write(pk)
        return filepath

    @staticmethod
    def _fake_json_file(filepath: t.Union[str, Path], content: t.Any = None) -> Path:
        filepath = filepath_validater(filepath)

        content = {"test": "fake json"} if content is None else content
        if isinstance(content, (list, dict, tuple)):
            ...
        elif isinstance(content, set):
            content = list(content)
        elif hasattr(content, '__dict__'):
            content = content.__dict__
        else:
            raise ValueError(f"unknown how to serial this type:{type(content)}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        return filepath

    @staticmethod
    def _fake_yaml_file(filepath: t.Union[str, Path], content: t.Any = None) -> Path:
        filepath = filepath_validater(filepath)
        content = {"test": "fake yaml file"} if content is None else content
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, encoding='utf-8')
        return filepath

    @staticmethod
    def _fake_img_file(filepath: t.Union[str, Path], content: t.Any = None) -> Path:
        """fake one image"""
        filepath = filepath_validater(filepath)
        content = str(content) if content is not None else filepath.name

        img = Image.new(mode='RGB', size=(120, 30), color=(255, 255, 255))
        draw = ImageDraw.Draw(img, mode='RGB')
        draw.text((0., 0.), content, 'red')

        with open(filepath, 'wb') as f:
            img.save(f)
        return filepath

    @staticmethod
    def _fake_tar_file(filepath: t.Union[str, Path], content: t.Any = None) -> Path:
        """fake tar"""
        filepath = filepath_validater(filepath)

        assert isinstance(content, list) or content is None, 'input should be a list'
        content = ["1.txt", '2.txt', '3.txt'] if content is None else content

        with tarfile.open(filepath, 'w') as t:
            for cont in content:
                tmp_dir = filepath.parent
                fp = tmp_dir.joinpath(cont if '.' in cont else str(content) + '.txt')
                with open(fp, 'w', encoding='utf-8') as f:
                    f.write(cont)

                t.add(fp, arcname=cont)

    @classmethod
    def fake(cls, filepath: t.Union[str, Path],
             *, f_suffix: str = None, content: t.Any = None, **kwargs) -> t.Optional[Path]:
        """
        pres support fake
        .txt .wav .json .yaml .tar
        (.jpg, .png, ...[any image type])

        Args:
            filepath: full path of file e.q. /home/xxx/x.txt
            f_suffix: file type e.q. txt (x.txt), wav
            content: file content to write into file. default auto write. validator in sub func

        Returns:
            pathlib.Path
        """
        filepath = filepath_validater(filepath)
        file_dir = filepath.parent
        file_dir.mkdir(parents=True, exist_ok=True)

        assert isinstance(f_suffix, str) or f_suffix is None, 'f_suffix should be str or None.like txt or wav'

        # get filename and file suffix e.q. xx.txt  -> xx  txt
        filename, suffix = None, None
        filename_cp = filepath.name.rsplit('.')
        if len(filename_cp) > 1:
            filename, suffix = '.'.join(filename_cp[:-1]), filename_cp[-1]
        elif filename_cp.__len__() == 1:
            filename = filename_cp[0]
            assert f_suffix is not None, "less of file type.like .txt"
            suffix = f_suffix if not f_suffix.startswith('.') else f_suffix[1:]
        else:
            raise ValueError(f"error filepath.{filepath}")
        assert filename is not None and suffix is not None, 'value error'

        filepath = filepath.parent.joinpath(f"{filename}.{suffix}")

        # fake any type
        if suffix == 'txt':
            cls._fake_txt_file(filepath, content)
        elif suffix == 'wav':
            cls._fake_wav_file(filepath, content, **kwargs)
        elif suffix == 'json':
            cls._fake_json_file(filepath, content)
        elif suffix in ('yaml', 'yml'):
            cls._fake_yaml_file(filepath, content)
        elif suffix == 'tar':
            cls._fake_tar_file(filepath, content)
        elif f".{suffix}" in list(cls.image_extension().keys()):
            cls._fake_img_file(filepath, content)
        else:
            raise TypeError(f"func not support fake this type of file. filename:[{filename}] type:[{suffix}]")
        return filepath if filepath.exists() else None


class DirFaker(Faker):
    """
    fake dir by dir info .
    fake file relay on (class FileFaker)
    """

    @classmethod
    def fake(cls, root: t.Union[str, Path], dir_info: t.Dict) -> bool:
        """

        Args:
            dir_info: e.q. {"dir1":{"dir2":["file1","file2]}
            root: thr root of new dir system e.q. root/dir1/dir2/file1 root/dir2/dir2/fil2

        Returns:
            ok bool
        """
        assert isinstance(dir_info, dict)
        filepath_validater(root)
        success = True
        new_dir = []
        try:
            for child, sub in dir_info.items():
                dir_path = root.joinpath(child)
                dir_path.mkdir(parents=True, exist_ok=True)
                new_dir.append(dir_path)
                if isinstance(sub, dict):
                    cls.fake(dir_path, sub)
                elif isinstance(sub, list):
                    for f in sub:
                        if '.' not in f:
                            continue
                        file_path = dir_path.joinpath(f)
                        if not file_path.exists():
                            FileFaker.fake(file_path)
        except Exception:  # noqa
            success = False
            for dir_ in new_dir:
                shutil.rmtree(dir_)
        return success
