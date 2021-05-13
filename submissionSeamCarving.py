
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# Edit SeamCarving.ipynb instead.
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, signal
from imageio import imread, imsave

def  rgb2gray(img):
    """
    Converts an RGB image into a greyscale image

    Input: ndarray of an RGB image of shape (H x W x 3)
    Output: ndarray of the corresponding grayscale image of shape (H x W)

    """

    if(img.ndim != 3 or img.shape[-1] != 3):
        print("Invalid image! Please provide an RGB image of the shape (H x W x 3) instead.".format(img.ndim))
        return None

    return np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])

def compute_gradients(img):
    """
    Computes the gradients of the input image in the x and y direction using a
    differentiation filter.

    ##########################################################################
    # TODO: Design a differentiation filter and update the docstring. Stick  #
    # to a pure differentiation filter for this assignment.                  #
    # Hint: Look at Slide 14 from Lecture 3: Gradients.                      #
    ##########################################################################

    Input: Grayscale image of shape (H x W)
    Outputs: gx, gy gradients in x and y directions respectively

    """

    ##########################################################################
    # TODO: Design a pure differentiation filter and use correlation to      #
    # compute the gradients gx and gy. You might have to try multiple        #
    # filters till the test below passes. All the tests after will fail if   #
    # this one does not pass.                                                #
    ##########################################################################
    #prewitt filter
    x_weights = [[-1,0,1],[-1,0,1],[-1,0,1]]
    y_weights = [[1,1,1], [0,0,0], [-1,-1,-1]]
    x_weights = np.flipud(np.fliplr(x_weights))
    gx = ndimage.correlate(img, x_weights, mode = "constant", cval = 0.0, origin = 0)
    # np.flipud(np.fliplr(gx))
    gy = ndimage.correlate(img, y_weights, mode = "constant", cval = 0.0, origin = 0)
    # np.flipud(np.fliplr(gy))

    return gx, gy


def energy_image(img):
    """
    Computes the energy of the input image according to the energy function:

        e(I) = abs(dI/dx) + abs(dI/dy)

    Use compute_gradients() to help you calculate the energy image. Remember to normalize energyImage by dividing it by max(energyImage).

    Input: image of the form (H x W) or (H x w x 3)
    Output: array of energy values of the image computed according to the energy function.

    """
      ##########################################################################
    # TODO: Compute the energy of input using the defined energy function.   #                                             #
    ##########################################################################
     # get shape
    energyImage = np.zeros_like(img)
    if img.ndim == 2:
        row, col = img.shape
    else:
        img = rgb2gray(img)
        row, col = img.shape

    #get gradient values
    gx, gy = compute_gradients(img)
    energyImage = np.zeros((row, col), dtype='float64')

    # compute using the function give
    for i in range(row):
        for j in range(col):
            energyImage[i][j] = abs(gx[i][j]) + abs(gy[i][j])

    # normalize energyImage by dividing it by max(energyImage)
    energyImage = energyImage/energyImage.max()

    return energyImage

def cumulative_minimum_energy_map(energyImage, seamDirection):
    """
    Calculates the cumulative minim energy map according to the function:

        M(i, j) = e(i, j) + min(M(i-1, j-1), M(i-1, j), M(i-1, j+1))

    Inputs:
        energyImage: Results of passign the input image to energy_image()
        seamDirection: 'HORIZONTAL' or 'VERTICAL'

    Output: cumulativeEnergyMap

    """
##########################################################################
    # TODO: Compute the cumulative minimum energy map in the input           #
    # seamDirection for the input energyImage. It is fine it is not fully    #
    # vectorized.                                                            #
    ##########################################################################

    if seamDirection == "HORIZONTAL":
        energyImage = energyImage.T
    # get shape
    row, col = energyImage.shape
    cumulativeEnergyMap = np.zeros((row, col), dtype='float64')
    cumulativeEnergyMap[0] = energyImage[0]

    for i in range(1, row):
        for j in range(col):
            #this calculates M(i-1, j-1)
            if j > 0:
                variable_one = cumulativeEnergyMap[i-1][j - 1]
            else:
                variable_one = cumulativeEnergyMap[i-1][j]

            # this calculates M(i-1, j)
            variable_two = cumulativeEnergyMap[i-1][j]

            # this calculates M(i-1, j+1)
            if j < col- 1:
                variable_three = cumulativeEnergyMap[i-1][j + 1]
            else:
                variable_three = cumulativeEnergyMap[i-1][j]

            # M(i, j) = e(i, j) + min(M(i-1, j-1), M(i-1, j), M(i-1, j+1))
            cumulativeEnergyMap[i][j] = energyImage[i][j] + min(variable_one, variable_two, variable_three)

    # Takes the transpose
    if seamDirection == "HORIZONTAL":
        cumulativeEnergyMap = cumulativeEnergyMap.T


    return cumulativeEnergyMap

def find_optimal_vertical_seam(cumulativeEnergyMap):
    """
    Finds the least connected vertical seam using a vertical cumulative minimum energy map.

    Input: Vertical cumulative minimum energy map.
    Output:
        verticalSeam: vector containing column indices of the pixels in making up the seam.

    """
##########################################################################
    # TODO: Find the minimal connected vertical seam using the input         #
    # cumulative minimum energy map.                                         #
    ##########################################################################

    #get shape
    row, col = cumulativeEnergyMap.shape

    #set up the basic variables
    verticalSeam = [] # the resultant array
    curr_min_column = 0 #stores the current minimum column
    curr_min_seam = cumulativeEnergyMap[row - 1][curr_min_column] #current minimal connected vertical seam

    # seam searching
    for j in range(1, col):
        if cumulativeEnergyMap[row - 1][j] < curr_min_seam:
            # new min is found
            curr_min_column = j
            curr_min_seam = cumulativeEnergyMap[row -1 ][curr_min_column]
    verticalSeam.append(curr_min_column)

    for i in range(row - 2, -1, -1):
        curr_min_seam = cumulativeEnergyMap[i][curr_min_column]
        for j in range(curr_min_column - 1, curr_min_column + 2):
            if j < col and j >= 0:
                if cumulativeEnergyMap[i][j] < curr_min_seam:
                    # new min is found
                    curr_min_column = j
                    curr_min_seam = cumulativeEnergyMap[i][curr_min_column]
        verticalSeam.append(curr_min_column)
        final_verticalSeam = verticalSeam[::-1] # final vertical seam found

    return final_verticalSeam

def find_optimal_horizontal_seam(cumulativeEnergyMap):
    """
    Finds the least connected horizontal seam using a horizontal cumulative minimum energy map.

    Input: Horizontal cumulative minimum energy map.
    Output:
        horizontalSeam: vector containing row indices of the pixels in making up the seam.

    """
    ##########################################################################
    # TODO: Find the minimal connected horizontal seam using the input       #
    # cumulative minimum energy map.                                         #
    ##########################################################################

    cumulativeEnergyMap = cumulativeEnergyMap.T
    row, col = cumulativeEnergyMap.shape

    horizontalSeam = []
    curr_min_column = 0
    curr_min_seam = cumulativeEnergyMap[row - 1][curr_min_column]

    for j in range(1, col):
        if cumulativeEnergyMap[row - 1][j] < curr_min_seam:
            curr_min_column = j
            curr_min_seam = cumulativeEnergyMap[row - 1][curr_min_column]

    horizontalSeam.append(curr_min_column)

    for i in range(row - 2, -1, -1):
        curr_min_seam = cumulativeEnergyMap[i][curr_min_column]
        for j in range(curr_min_column - 1, curr_min_column + 2):
            if j < col and j >= 0:

                if cumulativeEnergyMap[i][j] < curr_min_seam:
                    curr_min_column = j
                    curr_min_seam = cumulativeEnergyMap[i][curr_min_column]

        horizontalSeam.append(curr_min_column)
        final_horizontalSeam = horizontalSeam[::-1] # final horizontal seam found

    return final_horizontalSeam

def reduce_width(img, energyImage):
    """
    Removes pixels along a seam, reducing the width of the input image by 1 pixel.

    Inputs:
        img: RGB image of shape (H x W x 3) from which a seam is to be removed.
        energyImage: The energy image of the input image.

    Outputs:
        reducedColorImage: The input image whose width has been reduced by 1 pixel
        reducedEnergyImage: The energy image whose width has been reduced by 1 pixel
    """
    reducedEnergyImageSize = (energyImage.shape[0], energyImage.shape[1] - 1)
    reducedColorImageSize = (img.shape[0], img.shape[1] - 1, 3)
    print(reducedEnergyImageSize, reducedColorImageSize)

    reducedColorImage = np.zeros(reducedColorImageSize)
    reducedEnergyImage = np.zeros(reducedEnergyImageSize)

    ##########################################################################
    # TODO: Compute the cumulative minimum energy map and find the minimal   #
    # connected vertical seam. Then, remove the pixels along this seam.      #
    ##########################################################################
    # get image shape
    row, col, channels = img.shape

    # reducedColorImage = np.zeros((row, col - 1, channels))
    # reducedEnergyImage = np.zeros((row, col - 1))
    cumulativeEnergyMap = cumulative_minimum_energy_map(energyImage, "VERTICAL")
    verticalSeam = find_optimal_vertical_seam(cumulativeEnergyMap)

    for i in range(row):
        reducedColorImage[i, :verticalSeam[i], :] = img[i, :verticalSeam[i], ]
        reducedEnergyImage[i, :verticalSeam[i]] = energyImage[i, :verticalSeam[i]]

        reducedColorImage[i, verticalSeam[i]:] = img[i, verticalSeam[i] + 1:]
        reducedEnergyImage[i, verticalSeam[i]:] = energyImage[i, verticalSeam[i] + 1:]

    return reducedColorImage, reducedEnergyImage
    # return reducedColorImage, reducedEnergyImage

def reduce_height(img, energyImage):
    """
    Removes pixels along a seam, reducing the height of the input image by 1 pixel.

    Inputs:
        img: RGB image of shape (H x W x 3) from which a seam is to be removed.
        energyImage: The energy image of the input image.

    Outputs:
        reducedColorImage: The input image whose height has been reduced by 1 pixel
        reducedEnergyImage: The energy image whose height has been reduced by 1 pixel
    """

    reducedEnergyImageSize = tuple((energyImage.shape[0] - 1, energyImage.shape[1]))
    reducedColorImageSize = tuple((img.shape[0] - 1, img.shape[1], 3))

    reducedColorImage = np.zeros(reducedColorImageSize)
    reducedEnergyImage = np.zeros(reducedEnergyImageSize)

    ##########################################################################
    # TODO: Compute the cumulative minimum energy map and find the minimal   #
    # connected horizontal seam. Then, remove the pixels along this seam.    #
    ##########################################################################
    # get image shape
    row, col, channels = img.shape

    # reducedColorImage = np.zeros((row - 1, col, channels))
    # reducedEnergyImage = np.zeros((row - 1, col))
    cumulativeEnergyMap = cumulative_minimum_energy_map(energyImage, "HORIZONTAL")
    horizontalSeam = find_optimal_horizontal_seam(cumulativeEnergyMap)

    for i in range(col):

        reducedColorImage[:horizontalSeam[i], i, :] = img[:horizontalSeam[i], i, ]
        reducedEnergyImage[:horizontalSeam[i], i] = energyImage[:horizontalSeam[i], i]

        reducedColorImage[horizontalSeam[i]:, i] = img[horizontalSeam[i] + 1:, i]
        reducedEnergyImage[horizontalSeam[i]:, i] = energyImage[horizontalSeam[i] + 1:, i]



    return reducedColorImage, reducedEnergyImage
    # return reducedColorImage, reducedEnergyImage

def seam_carving_reduce_width(img, reduceBy):
    """
    Reduces the width of the input image by the number pixels passed in reduceBy.

    Inputs:
        img: Input image of shape (H x W X 3)
        reduceBy: Positive non-zero integer indicating the number of pixels the width
        should be reduced by.

    Output:
        reducedColorImage: The result of removing reduceBy number of vertical seams.
    """

    reducedColorImage = img[:, reduceBy//2:-reduceBy//2, :]  #crops the image

    ##########################################################################
    # TODO: For the Prague image, write a few lines of code to call the      #
    # we have written to find and remove 100 vertical seams                  #
    ##########################################################################
    for i in range (reduceBy):
        reducedColorImage, energyImage = reduce_width(reducedColorImage, energy_image(reducedColorImage))
    reducedColorImage = np.uint8(reducedColorImage)
    return reducedColorImage


def seam_carving_reduce_height(img, reduceBy):
    """
    Reduces the height of the input image by the number pixels passed in reduceBy.

    Inputs:
        img: Input image of shape (H x W X 3)
        reduceBy: Positive non-zero integer indicating the number of pixels the
        height should be reduced by.

    Output:
        reducedColorImage: The result of removing reduceBy number of horizontal
        seams.
    """

    reducedColorImage = img[reduceBy//2:-reduceBy//2, :, :]  #crops the image

    ##########################################################################
    # TODO: For the Prague image, write a few lines of code to call the      #
    # we have written to find and remove 100 horizontal seams.               #
    ##########################################################################
    for i in range (reduceBy):
        reducedColorImage, energyImage = reduce_height(reducedColorImage, energy_image(reducedColorImage))
    reducedColorImage = np.uint8(reducedColorImage)

    return reducedColorImage