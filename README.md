# .btf.npz helper
Extract .btf.npz archive format.

Extract to ndarray compatible with openCV(BGR, channels-last).


## Install
```bash
pip install git+https://github.com/2-propanol/btfnpz_helper
```

## Example
```python
>>> from btfnpz import Btfnpz

>>> btf = Btfnpz("sample.zip")
>>> print(btf.img_shape)
(512, 512, 3)
>>> angles_list = list(btf.angles_set)
>>> image = btf.angles_to_image(*angles_list[0])
>>> print(image.shape)
(512, 512, 3)
>>> print(angles_list[0])
(15.0, 0.0, 0.0, 0.0)
```
