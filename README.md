# BTF helper
Extract home-brewed BTF format.

Extract to ndarray compatible with openCV(BGR, channels-last).


## Install
```bash
pip install git+https://github.com/2-propanol/BTF_helper
```

## Example
```python
>>> from btf_helper import Btfnpz

>>> btf = Btfnpz("example.zip")
>>> print(btf.img_shape)
(512, 512, 3)
>>> angles_list = list(btf.angles_set)
>>> image = btf.angles_to_image(*angles_list[0])
>>> print(image.shape)
(512, 512, 3)
>>> print(angles_list[0])
(15.0, 0.0, 0.0, 0.0)
```
