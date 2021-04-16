import numpy as np


class Btfnpz:
    """.btf.npzファイルから角度や画像を取り出す

    角度は全て度数法(degree)を用いている。
    .btf.npzファイルに含まれる角度情報の順番は保証せず、並べ替えもしない。
    `angles_set`には`list`ではなく、順序の無い`set`を用いている。

    画像の実体はopencvと互換性のあるndarray形式(BGR, channels-last)で出力する。

    .btf.npzファイル要件:
        `np.savez`もしくは`np.saves_compressed`で
        画像を`images`、角度情報を`angles`のキーワード引数で格納している.btf.npzファイル。

    Attributes:
        npz_filepath (str): コンストラクタに指定した.btf.npzファイルパス。
        img_shape (tuple[int,int,int]): btfファイルに含まれている画像のshape。
        angles_set (set[tuple[float,float,float,float]]):
            .btf.npzファイルに含まれる画像の角度条件の集合。

    Example:
        >>> btf = Btfnpz("reference.btf")
        >>> print(btf.img_shape)
        (512, 512, 3)
        >>> angles_list = list(btf.angles_set)
        >>> image = btf.angles_to_image(*angles_list[0])
        >>> print(image.shape)
        (512, 512, 3)
        >>> print(angles_list[0])
        (45.0, 255.0, 0.0, 0.0)
    """

    def __init__(self, npz_filepath: str) -> None:
        """使用するzipファイルを指定する"""
        self.npz_filepath = npz_filepath

        self.__npz = np.load(npz_filepath)
        self.images_list = self.__npz["images"]
        self.images_list.flags.writeable = False
        self.angles_list = self.__npz["angles"]
        self.angles_list.flags.writeable = False
        del self.__npz

        self.img_shape = self.images_list.shape[1:]

        self.angles_set = frozenset(
            {tuple(angles) for angles in self.angles_list}
        )

    def angles_to_image(self, tl: int, pl: int, tv: int, pv: int) -> np.ndarray:
        """`tl`, `pl`, `tv`, `pv`の角度条件の画像をndarray形式で返す"""
        for i, angles in enumerate(self.angles_list):
            if np.allclose(angles, np.array((tl, pl, tv, pv))):
                return self.images_list[i]
        raise ValueError(f"tl:{tl}, pl:{pl}, tv:{tv}, pv:{pv} not found")
