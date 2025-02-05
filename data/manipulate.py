import torch
from torch.utils.data import Dataset

#CREATE DATASET CLASSES

class FeatureDataset(Dataset):
    def __init__(self, input_tensors, label):
        super().__init__()
        self.input_tensors = input_tensors
        self.label = label

    def __len__(self):
        return self.input_tensors.shape[0]

    def __getitem__(self, index):
        sample = self.input_tensors[index]
        return (sample, self.label)


class CustomDataset(Dataset):
    '''To create a PyTorch dataset from provided numpy-arrays.'''

    def __init__(self, x1, x2, y):
        super().__init__()
        self.x1 = x1
        self.x2 = x2
        self.y = y

    def __len__(self):
        return len(self.x1)

    def __getitem__(self, index):
        return torch.tensor((self.x1[index], self.x2[index])), int(self.y[index])


class ReducedDataset(Dataset):
    '''To reduce a dataset, taking only samples corresponding to provided indices.
    This is useful for splitting a dataset into a training and validation set.'''

    def __init__(self, original_dataset, indeces):
        super().__init__()
        self.dataset = original_dataset
        self.indeces = indeces

    def __len__(self):
        return len(self.indeces)

    def __getitem__(self, index):
        return self.dataset[self.indeces[index]]


class SubDataset(Dataset):
    '''To sub-sample a dataset, taking only those samples with label in [sub_labels]. eg labels of class 2 and 3

    After this selection of samples has been made, it is possible to transform the target-labels,
    which can be useful when doing continual learning with fixed number of output units.'''

    def __init__(self, original_dataset, sub_labels, target_transform=None):
        super().__init__()
        self.dataset = original_dataset
        self.sub_indeces = []
        for index in range(len(self.dataset)):
            if hasattr(original_dataset, "targets"): #The hasattr() function returns True if the specified object has the specified attribute, otherwise False .
                if self.dataset.target_transform is None:
                    label = self.dataset.targets[index]
                else:
                    label = self.dataset.target_transform(self.dataset.targets[index]) #you can see that transform and target_transform are used to modify / augment / transform the image and the target respectively.
            else:
                label = self.dataset[index][1]
            if label in sub_labels:
                self.sub_indeces.append(index) #append to list if labels is the ones we want
        self.target_transform = target_transform

    def __len__(self):
        return len(self.sub_indeces)

    def __getitem__(self, index):
        sample = self.dataset[self.sub_indeces[index]]
        if self.target_transform:
            target = self.target_transform(sample[1])
            sample = (sample[0], target)
        return sample


class TransformedDataset(Dataset):
    '''To modify an existing dataset with a transform.
    This is useful for creating different permutations of MNIST without loading the data multiple times.'''

    def __init__(self, original_dataset, transform=None, target_transform=None):
        super().__init__()
        self.dataset = original_dataset
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        (input, target) = self.dataset[index]
        if self.transform:
            input = self.transform(input)
        if self.target_transform:
            target = self.target_transform(target)
        return (input, target)


#----------------------------------------------------------------------------------------------------------#


class UnNormalize(object):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        """Denormalize image, either single image (C,H,W) or image batch (N,C,H,W)"""
        batch = (len(tensor.size())==4)
        for t, m, s in zip(tensor.permute(1,0,2,3) if batch else tensor, self.mean, self.std):
            t.mul_(s).add_(m)
            # The normalize code -> t.sub_(m).div_(s)
        return tensor
