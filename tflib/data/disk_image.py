from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import multiprocessing

import tensorflow as tf
from tflib.data.dataset import batch_dataset, Dataset


_N_CPU = multiprocessing.cpu_count()


def disk_image_batch_dataset(img_paths, batch_size, labels=None, prefetch_batch=_N_CPU + 1, drop_remainder=True, filter=None,
                             map_func=None, num_threads=_N_CPU, shuffle=True, buffer_size=4096, repeat=-1):
    """Disk image batch dataset.

    This function is suitable for jpg and png files

    img_paths: string list or 1-D tensor, each of which is an iamge path
    labels: label list/tuple_of_list or tensor/tuple_of_tensor, each of which is a corresponding label
    """
    if labels is None:
        dataset = tf.data.Dataset.from_tensor_slices(img_paths)
    elif isinstance(labels, tuple):
        dataset = tf.data.Dataset.from_tensor_slices((img_paths,) + tuple(labels))
    else:
        dataset = tf.data.Dataset.from_tensor_slices((img_paths, labels))

    def parse_func(path, *label):
        img = tf.read_file(path)
        img = tf.image.decode_png(img, 3)
        return (img,) + label

    if map_func:
        def map_func_(*args):
            return map_func(*parse_func(*args))
    else:
        map_func_ = parse_func

    # dataset = dataset.map(parse_func, num_parallel_calls=num_threads) is slower

    dataset = batch_dataset(dataset, batch_size, prefetch_batch, drop_remainder, filter,
                            map_func_, num_threads, shuffle, buffer_size, repeat)

    return dataset


class DiskImageData(Dataset):
    """DiskImageData.

    This function is suitable for jpg and png files

    img_paths: string list or 1-D tensor, each of which is an iamge path
    labels: label list or tensor, each of which is a corresponding label
    """

    def __init__(self, img_paths, batch_size, labels=None, prefetch_batch=_N_CPU + 1, drop_remainder=True, filter=None,
                 map_func=None, num_threads=_N_CPU, shuffle=True, buffer_size=4096, repeat=-1, sess=None):
        super(DiskImageData, self).__init__()
        dataset = disk_image_batch_dataset(img_paths, batch_size, labels, prefetch_batch, drop_remainder, filter,
                                           map_func, num_threads, shuffle, buffer_size, repeat)
        self._bulid(dataset, sess)
