# BTF helper
Extract home-brewed BTF format.

Extract to ndarray compatible with openCV(BGR, channels-last).


## Install
```bash
pip install git+https://github.com/2-propanol/BTF_helper
```

## Example
```python
>>> from btf_helper import Btfnpz, Btfzip

>>> btf = Btfnpz("example.btf.npz")
>>> print(btf.img_shape)
(512, 512, 3)
>>> angles_list = list(btf.angles_set)
>>> image = btf.angles_to_image(*angles_list[0])
>>> print(image.shape)
(512, 512, 3)
>>> print(angles_list[0])
(15.0, 0.0, 0.0, 0.0)

>>> btf = Btfzip("example.zip", file_ext=".exr", angle_sep="_")
>>> print(btf.img_shape)
(512, 512, 3)
>>> angles_list = list(btf.angles_set)
>>> image = btf.angles_to_image(*angles_list[0])
>>> print(image.shape)
(512, 512, 3)
>>> print(angles_list[0])
(15.0, 0.0, 0.0, 0.0)
```

## Other utilities
### Downsampling
[Gist :downsampling.py](https://gist.github.com/2-propanol/177fe97b9169e28a9498a2a4ab849a8a)
> Create a new `.btfzip` containing the resized and cropped BTF data from another `.btfzip`.
