from pprint import pprint
import shutil
from PIL import Image, ImageFile
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import os


def check_category_directories():
    categories = [
        'red',
        'green',
        'blue',
        'cyan',
        'magenta',
        'yellow',
        'pastel',
        'black and white',
        'dark',
        'other',
    ]
    for category in categories:
        if not os.path.isdir(category):
            os.mkdir(category)


def get_dominant_colors(filename, NUM_CLUSTERS):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # print ('reading image')
    input_image = Image.open(filename)
    input_image = input_image.resize((150, 150))      # optional, to reduce time
    image_array = np.asarray(input_image) # convert image to array
    shape = image_array.shape 
    # reshape array to merge color bands
    if len(shape) > 2:
        image_array = image_array.reshape(scipy.product(shape[:2]), shape[2])

    # get clusters
    # print ('finding clusters')
    codes, _ = scipy.cluster.vq.kmeans(image_array.astype(float), NUM_CLUSTERS)
    # print( 'cluster centres:\n', codes)

    # vector quatisation
    vecs, _ = scipy.cluster.vq.vq(image_array, codes) # assign codes

    # find most frequent        
    counts, _ = scipy.histogram(vecs, len(codes)) # count occurrences
    index_max = scipy.argmax(counts) 
    peak = codes[index_max]
    color = []
    for c in peak:
        color.append(int(c))
    rgb_color = color
    hex_color = '%02x%02x%02x' % (color[0], color[1], color[2])
    decimal_color = int(hex_color, 16)
    return hex_color, rgb_color, decimal_color


def sort_images(files_list, NUM_CLUSTERS):
    check_category_directories()

    i = 0
    for file in files_list:
        os.system('cls')
        i += 1
        print('-'*80)
        print('processing image {} of {}...'.format(i, len(files)))
        print('-'*80)
        dominant_hex, dominant_rgb, dominant_decimal = get_dominant_colors(file, NUM_CLUSTERS)

        filename, file_extension = os.path.splitext(file)
        
        try: 
            new_filename = '{}{}'.format(dominant_hex, file_extension)
            os.rename(file, new_filename)
        except FileExistsError:
            new_filename = '{}{}{}'.format(dominant_hex, i, file_extension)
            os.rename(file, new_filename)

        percent_range = 0.2
        pastel_limit = 180


        # greyscale
        if dominant_rgb[0] == dominant_rgb[1] == dominant_rgb[2]: 
            shutil.copy(new_filename, 'black and white')

        # pastel
        elif dominant_rgb[0] >= pastel_limit and  dominant_rgb[1] >= pastel_limit and  dominant_rgb[2] >= pastel_limit:
            shutil.copy(new_filename, 'pastel')

        # blue more than red but less than green (green to cyan)
        elif dominant_rgb[2] > dominant_rgb[0] and dominant_rgb[2] < dominant_rgb[1]:
            shutil.copy(new_filename, 'cyan')

        # blue more than green but less than red (red to magenta)
        elif dominant_rgb[2] > dominant_rgb[1] and dominant_rgb[2] < dominant_rgb[0]:
            shutil.copy(new_filename, 'magenta')

        # green more than red but less than blue (blue to cyan)
        elif dominant_rgb[1] > dominant_rgb[0] and dominant_rgb[1] < dominant_rgb[2]:
            shutil.copy(new_filename, 'cyan')
        
        # green more than blue but less than  red (red to yellow)
        elif dominant_rgb[1] > dominant_rgb[2] and dominant_rgb[1] < dominant_rgb[0]:
            shutil.copy(new_filename, 'yellow')
        
        # red more than green but less than blue (blue to magenta)
        elif dominant_rgb[0] > dominant_rgb[1] and dominant_rgb[0] < dominant_rgb[2]:
            shutil.copy(new_filename, 'magenta')

        # red more than blue but less than green (green to yellow)
        elif dominant_rgb[0] > dominant_rgb[2] and dominant_rgb[0] < dominant_rgb[1]:
            shutil.copy(new_filename, 'yellow')

        # mostly red
        elif dominant_rgb[0] > (dominant_rgb[1]-int(dominant_rgb[1]*percent_range)) and dominant_rgb[0] > (dominant_rgb[2]-int(dominant_rgb[2]*percent_range)): 
            shutil.copy(new_filename, 'red')

        # mostly green (green more than red and blue)
        elif dominant_rgb[1] > (dominant_rgb[0]-int(dominant_rgb[0]*percent_range)) and dominant_rgb[1] > (dominant_rgb[2]-int(dominant_rgb[2]*percent_range)): 
            shutil.copy(new_filename, 'green')

        #mostly blue (blue more than green and red)
        elif dominant_rgb[2] > (dominant_rgb[0]-int(dominant_rgb[0]*percent_range)) and dominant_rgb[2] > (dominant_rgb[1]-int(dominant_rgb[1]*percent_range)): 
            shutil.copy(new_filename, 'blue')
        
        # dark
        elif dominant_rgb[0] <= 40 and  dominant_rgb[1] <= 40 and  dominant_rgb[2] <= 40:
            shutil.copy(new_filename, 'dark')

        else:
            shutil.copy(new_filename, 'other')


if __name__ == "__main__":
    NUM_CLUSTERS = 2

    path_to_images = input('please paste the path to the image directory\n')

    os.chdir(path_to_images)

    files = next(os.walk(path_to_images))[2]
    # pprint(files)
    
    sort_images(files, NUM_CLUSTERS)
