# -*- coding: utf-8 -*-
""" Estimate pose by chainer. """

import numpy as np
from chainer import serializers

from modules.dataset_indexing.chainer import PoseDataset
from modules.models.chainer import AlexNet


class PoseEstimator(object):
    """ Estimate pose using pose net trained by chainer.

    Args:
        Nj (int): Number of joints.
        model_file (str): Model parameter file.
        filename (str): Image-pose list file.
    """

    def __init__(self, Nj, model_file, filename):
        # initialize model to estimate.
        self.model = AlexNet(Nj)
        serializers.load_npz(model_file, self.model)
        # load dataset to estimate.
        self.dataset = PoseDataset(filename)

    def get_dataset_size(self):
        """ Get size of dataset. """
        return len(self.dataset)

    def estimate(self, index):
        """ Estimate pose of i-th image. """
        image, _, _ = self.dataset.get_example(index)
        self.model.predict(np.array([image]))