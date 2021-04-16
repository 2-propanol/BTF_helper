import numpy as np


class Btfnpz:
    """.btf.npzファイルから角度や画像を取り出す

    角度は全て度数法(degree)を用いている。
    .btf.npzファイルに含まれる角度情報の並べ替えはしない。
    角度情報の取得には`angles_set`(Pythonの`set`)の他、
    `angles_list`(`flags.writeable`を`False`にセットした`np.ndarray`)が利用できる。

    画像の実体はopencvと互換性のあるndarray形式(BGR, channels-last)で出力する。

    .btf.npzファイル要件:
        `np.savez`もしくは`np.savez_compressed`で
        画像を`images`、角度情報を`angles`のキーワード引数で格納している.btf.npzファイル。

    Attributes:
        npz_filepath (str): コンストラクタに指定した.btf.npzファイルパス。
        img_shape (tuple[int,int,int]): btfファイルに含まれている画像のshape。
        angles_set (set[tuple[float,float,float,float]]):
            .btf.npzファイルに含まれる画像の角度条件の集合。

    Example:
        >>> btf = Btfnpz("example.btf")
        >>> print(btf.img_shape)
        (512, 512, 3)
        >>> angles_list = list(btf.angles_set)
        >>> print(angles_list[0])
        (45.0, 255.0, 0.0, 0.0)
        >>> print(btf.angles_list[0])
        (45.0, 255.0, 0.0, 0.0)
        >>> image = btf.angles_to_image(*angles_list[0])
        >>> print(image.shape)
        (512, 512, 3)
        >>> print(btf.image_list[0].shape)
        (512, 512, 3)
    """

    def __init__(self, npz_filepath: str) -> None:
        """使用するzipファイルを指定する"""
        self.npz_filepath = npz_filepath

        self.__npz = np.load(npz_filepath)
        self.image_list = self.__npz["images"]
        self.image_list.flags.writeable = False
        self.angles_list = self.__npz["angles"]
        self.angles_list.flags.writeable = False
        del self.__npz

        self.img_shape = self.image_list.shape[1:]

        self.angles_set = frozenset({tuple(angles) for angles in self.angles_list})

    def angles_to_image(self, tl: float, pl: float, tv: float, pv: float) -> np.ndarray:
        """`tl`, `pl`, `tv`, `pv`の角度条件の画像をndarray形式で返す"""
        for i, angles in enumerate(self.angles_list):
            if np.allclose(angles, np.array((tl, pl, tv, pv))):
                return self.image_list[i]
        raise ValueError(
            f"condition ({tl}, {pl}, {tv}, {pv}) does not exist in '{self.npz_filepath}'."
        )
