#!/usr/bin/env python

import os
import sys
import cv2
import numpy as np

def normalize(X, low, high, dtype=None):
    """Normalizes a given array in X to a value between low and high."""
    X = np.asarray(X)
    minX, maxX = np.min(X), np.max(X)
    # normalize to [0...1].
    X = X - float(minX)
    X = X / float((maxX - minX))
    # scale to [low...high].
    X = X * (high-low)
    X = X + low
    if dtype is None:
        return np.asarray(X)
    return np.asarray(X, dtype=dtype)


def read_images(path, sz=None):
    c = 0
    X,y = [], []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                    # resize to given size (if given)
                    if (sz is not None):
                        im = cv2.resize(im, sz)
                    # print subdirname,filename
                    X.append(np.asarray(im, dtype=np.uint8))
                    y.append(c)
                except IOError, (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
            print "Subdir: {0} Label: {1}".format(subdirname,c) 
            c = c+1
    return [X,y]

if __name__ == "__main__":
    # This is where we write the images, if an output_dir is given
    # in command line:
    out_dir = None
    # You'll need at least a path to your image data, please see
    # the tutorial coming with this source code on how to prepare
    # your image data:
    if len(sys.argv) < 3:
        print "USAGE: facerec_demo.py </path/to/images> sampleImage"
        sys.exit()
    # Now read in the image data. This must be a valid path!
    [X,y] = read_images(sys.argv[1])
    sampleImagePath=sys.argv[2]
    # Convert labels to 32bit integers. This is a workaround for 64bit machines,
    # because the labels will truncated else. This will be fixed in code as
    # soon as possible, so Python users don't need to know about this.
    # Thanks to Leo Dirac for reporting:
    y = np.asarray(y, dtype=np.int32)
    # If a out_dir is given, set it:
    # Create the Eigenfaces model. We are going to use the default
    # parameters for this simple example, please read the documentation
    # for thresholding:
    model = cv2.createLBPHFaceRecognizer()
    # Read
    # Learn the model. Remember our function returns Python lists,
    # so we use np.asarray to turn them into NumPy lists to make
    # the OpenCV wrapper happy:
    model.train(np.asarray(X), np.asarray(y))
    model.save('model-data.yml')
    # We now get a prediction from the model! In reality you
    # should always use unseen images for testing your model.
    # But so many people were confused, when I sliced an image
    # off in the C++ version, so I am just using an image we
    # have trained with.
    #
    # model.predict is going to return the predicted label and
    # the associated confidence:
    
    im = cv2.imread(sampleImagePath, cv2.IMREAD_GRAYSCALE)
    [p_label, p_confidence] = model.predict(im)
    
    #np.asarray(testImage, dtype=np.uint8)
    #[p_label, p_confidence] = model.predict(np.asarray(testImage, dtype=np.uint8))
    #[p_label, p_confidence] = model.predict(testImage)
    # Print it:
    print "Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence)
    cv2.imshow('sample',im);
    cv2.imshow('guess',X[p_label*10])
    cv2.waitKey(0)

