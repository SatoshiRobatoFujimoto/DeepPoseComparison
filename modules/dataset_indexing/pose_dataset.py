# -*- coding: utf-8 -*-
""" Pose dataset indexing. """

import random
import numpy as np
from PIL import Image
from chainer import dataset


class PoseDataset(dataset.DatasetMixin):
    """ Pose dataset indexing.

    Args:
        path (str): A path to dataset.
        data_augmentation (bool): True for data augmentation.
        ksize (int): Size of filter.
        stride (int): Stride of filter applications.
    """

    def __init__(self, path, data_augmentation=True, ksize=11, stride=4):
        self.path = path
        self.data_augmentation = data_augmentation
        self.ksize = ksize
        self.stride = stride
        # load dataset.
        self.images, self.poses, self.visibilities = self._load_dataset()

    def __len__(self):
        return len(self.images)

    def get_example(self, i):
        """ Returns the i-th example. """
        image = self._read_image(self.images[i])
        pose = self.poses[i]
        visibility = self.visibilities[i]
        # data augumentation.
        if self.data_augmentation:
            image, pose = self._random_crop(image, pose)
            image = self._random_noise(image)
        # scale to [0, 1].
        image /= 255.
        return image, pose, visibility

    def _load_dataset(self):
        images = []
        poses = []
        visibilities = []
        for line in open(self.path):
            line_split = line[:-1].split(',')
            images.append(line_split[0])
            x = np.array(line_split[1:])
            x = x.reshape(-1, 3)
            poses.append(x[:, :2].astype(np.float32))
            visibilities.append(x[:, 2].astype(np.int32))
        return images, poses, visibilities

    @staticmethod
    def _read_image(path):
        f = Image.open(path)
        try:
            image = np.asarray(f, dtype=np.float32)
        finally:
            f.close()
        return image.transpose(2, 0, 1)

    def _random_crop(self, image, pose):
        p_min = np.min(pose, 0)
        p_max = np.max(pose, 0)
        _, h, w = image.shape
        shape = (w, h)
        crop_min = [0, 0]
        crop_max = [0, 0]
        # crop image.
        for i in range(2):
            residual = shape[i] - max(np.ceil(p_max[i] - p_min[i]) + 3, self.ksize)
            random_all = random.randint(0, residual)/self.stride*self.stride
            crop_min[i] = random.randint(
                max(0, int(np.floor(p_max[i])) - (shape[i] - random_all) + 2),
                min(int(np.floor(p_min[i])) - 1, random_all))
            crop_max[i] = shape[i] - (random_all - crop_min[i])
        image = image[:, crop_min[1]:crop_max[1], crop_min[0]:crop_max[0]]
        # modify pose according to the cropping.
        pose = pose - crop_min
        # return augmented data.
        return image, pose

    @staticmethod
    def _random_noise(image):
        image = image.copy()
        # add random noise to keep eigen value.
        C = np.cov(np.reshape(image, (3, -1)))
        l, e = np.linalg.eig(C)
        p = np.random.normal(0, 0.1)*np.matrix(e).T*np.sqrt(np.matrix(l)).T
        for c in range(3):
            image[c] += p[c]
        image = np.clip(image, 0, 255)
        # return augmented data.
        return image
