from collections import Counter
from decimal import Decimal
from sys import stderr
from typing import Tuple
from zipfile import ZipFile

import cv2
import numpy as np
from simplejpeg import decode_jpeg

# PEP484 -- Type Hints:
#   Type Definition Syntax:
#     The numeric tower:
#       when an argument is annotated as having type `float`,
#       an argument of type `int` is acceptable


class Btfzip:
    """画像ファイルを格納したzipファイルから角度と画像を取り出す（小数点角度と画像拡張子指定対応）

    角度は全て度数法(degree)を用いている。
    zipファイルに含まれる角度情報の順番は保証せず、並べ替えもしない。
    `angles_set`には`list`ではなく、順序の無い`set`を用いている。

    画像の実体はopencvと互換性のあるndarray形式(BGR, channels-last)で出力する。

    zipファイル要件:
        f"tl{float}{angle_sep}pl{float}{angle_sep}tv{float}{angle_sep}pv{float}.{file_ext}"
        を格納している。
        例) "tl20.25_pl10_tv11.5_pv0.exr"

    Attributes:
        zip_filepath (str): コンストラクタに指定したzipファイルパス。
        angles_set (set[tuple[float,float,float,float]]):
            zipファイルに含まれる画像の角度条件の集合。

    Example:
        >>> btf = Btfzip("Colorchecker.zip")
        >>> angles_list = list(btf.angles_set)
        >>> image = btf.angles_to_image(*angles_list[0])
        >>> print(image.shape)
        (256, 256, 3)
        >>> print(angles_list[0])
        (0, 0, 0, 0)
    """

    def __init__(
        self, zip_filepath: str, file_ext: str = ".exr", angle_sep: str = " "
    ) -> None:
        """使用するzipファイルを指定する

        指定したzipファイルに角度条件の重複がある場合、
        何が重複しているか表示し、`RuntimeError`を投げる。
        """
        self.zip_filepath = zip_filepath
        self.__z = ZipFile(zip_filepath)
        # NOTE: ARIES4軸ステージの分解能は0.001度
        self.DECIMAL_PRECISION = Decimal("1E-3")

        # ファイルパスは重複しないので`filepath_set`はsetで良い
        filepath_set = {path for path in self.__z.namelist() if path.endswith(file_ext)}
        self.__angles_vs_filepath_dict = {
            self._filename_to_angles(path, angle_sep): path for path in filepath_set
        }
        self.angles_set = frozenset(self.__angles_vs_filepath_dict.keys())

        # 角度条件の重複がある場合、何が重複しているか調べる
        if len(filepath_set) != len(self.angles_set):
            angles_list = [self._filename_to_angles(path) for path in filepath_set]
            angle_collection = Counter(angles_list)
            for angles, counter in angle_collection.items():
                if counter > 1:
                    print(
                        f"[BTF-Helper] '{self.zip_filepath}' has"
                        + f"{counter} files with condition {angles}.",
                        file=stderr,
                    )
            raise RuntimeError(f"'{self.zip_filepath}' has duplicated conditions.")

        if file_ext == ".jpg" or file_ext == ".jpeg":
            self.angles_to_image = self._angles_to_image_simplejpeg
        else:
            self.angles_to_image = self._angles_to_image_cv2

    def _filename_to_angles(
        self, filename: str, sep: str
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """ファイル名(orパス)から角度(`Decimal`)のタプル(`tl`, `pl`, `tv`, `pv`)を取得する"""
        angles = filename.split("/")[-1][:-4].split(sep)
        try:
            tl = Decimal(angles[0][2:]).quantize(self.DECIMAL_PRECISION)
            pl = Decimal(angles[1][2:]).quantize(self.DECIMAL_PRECISION)
            tv = Decimal(angles[2][2:]).quantize(self.DECIMAL_PRECISION)
            pv = Decimal(angles[3][2:]).quantize(self.DECIMAL_PRECISION)
        except ValueError as e:
            raise ValueError("invalid angle:", angles) from e
        return (tl, pl, tv, pv)

    def _angles_to_image_cv2(
        self, tl: float, pl: float, tv: float, pv: float
    ) -> np.ndarray:
        """`tl`, `pl`, `tv`, `pv`の角度条件の画像をndarray形式で返す

        `filename`が含まれるファイルが存在しない場合は`ValueError`を投げる。
        """
        key = (
            Decimal(tl).quantize(self.DECIMAL_PRECISION),
            Decimal(pl).quantize(self.DECIMAL_PRECISION),
            Decimal(tv).quantize(self.DECIMAL_PRECISION),
            Decimal(pv).quantize(self.DECIMAL_PRECISION),
        )
        filepath = self.__angles_vs_filepath_dict.get(key)
        if not filepath:
            raise ValueError(
                f"Condition {key} does not exist in '{self.zip_filepath}'."
            )

        with self.__z.open(filepath) as f:
            return cv2.imdecode(
                np.frombuffer(f.read(), np.uint8),
                cv2.IMREAD_ANYDEPTH + cv2.IMREAD_ANYCOLOR,
            )

    def _angles_to_image_simplejpeg(
        self, tl: float, pl: float, tv: float, pv: float
    ) -> np.ndarray:
        """`tl`, `pl`, `tv`, `pv`の角度条件の画像をndarray形式で返す

        `filename`が含まれるファイルが存在しない場合は`ValueError`を投げる。
        """
        key = (
            Decimal(tl).quantize(self.DECIMAL_PRECISION),
            Decimal(pl).quantize(self.DECIMAL_PRECISION),
            Decimal(tv).quantize(self.DECIMAL_PRECISION),
            Decimal(pv).quantize(self.DECIMAL_PRECISION),
        )
        filepath = self.__angles_vs_filepath_dict.get(key)
        if not filepath:
            raise ValueError(
                f"Condition {key} does not exist in '{self.zip_filepath}'."
            )

        with self.__z.open(filepath) as f:
            return decode_jpeg(f.read(), colorspace="BGR")
