from typing import Sequence, List, Tuple, Any, Union, Iterable

import numpy as np

from nebullvm.utils.onnx import convert_to_numpy


class DataManager:
    """Class for managing the user data in nebullvm.

    Attributes:
        data_reader(Sequence): Object implementing the __getitem__, the
            __len__ and the __iter__/__next__ APIs. It should read the
            user data and return tuples of tensors for feeding the models.
    """

    def __init__(self, data_reader: Sequence):
        self._data_reader = data_reader
        self._pointer = 0

    def __getitem__(self, item):
        return self._data_reader[item]

    def __len__(self):
        return len(self._data_reader)

    def __iter__(self):
        self._pointer = 0
        return self

    def __next__(self):
        if self._pointer < len(self):
            data = self[self._pointer]
            self._pointer += 1
            return data
        else:
            raise StopIteration

    def get_numpy_list(
        self, n: int, shuffle: bool = False, with_ys: bool = False
    ) -> Union[
        List[Tuple[np.ndarray, ...]], Tuple[List[Tuple[np.ndarray, ...]], List]
    ]:
        if not with_ys:
            return [
                tuple(convert_to_numpy(x) for x in tuple_)
                for tuple_ in self.get_list(n, shuffle)
            ]
        else:
            xs, ys = self.get_list(n, shuffle, with_ys=True)
            return [
                tuple(convert_to_numpy(x) for x in tuple_) for tuple_ in xs
            ], ys

    def get_list(
        self, n: int, shuffle: bool = False, with_ys: bool = False
    ) -> Union[List[Tuple[Any, ...]], Tuple[List[Tuple[Any, ...]], List]]:
        if shuffle:
            idx = np.random.choice(len(self), n, replace=n > len(self))
        else:
            idx = np.arange(0, min(n, len(self)))
            if n > len(self):
                idx = np.concatenate(
                    [
                        idx,
                        np.random.choice(
                            len(self), n - len(self), replace=True
                        ),
                    ]
                )
        if not with_ys:
            return [self[i][0] for i in idx]

        ys, xs = [], []
        for i in idx:
            x, y = self[i]
            xs.append(x)
            ys.append(y)
        return xs, ys

    @classmethod
    def from_iterable(cls, iterable: Iterable, max_length: int = 500):
        return cls([x for i, x in enumerate(iterable) if i < max_length])
