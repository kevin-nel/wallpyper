import shutil
from PIL import Image, ImageFile
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import os
from numba import jit


@jit(nopython=True)
def check_category_directories():
    path_to_images = input("please paste the path to the image directory\n")
    os.chdir(path_to_images)
    categories = [
        "red",
        "green",
        "blue",
        "cyan",
        "magenta",
        "yellow",
        "pastel",
        "black and white",
        "dark",
        "other",
    ]
    for file_name in os.listdir("."):
        if not file_name.endswith(".jpg") or not file_name.endswith(".png"):
            print(
                "there are no supported image files in the current directory\n"
                "please select another directory"
            )
            check_category_directories()
        else:
            break

    if os.path.curdir in categories:
        if (
            input(
                'there is currently a directory named "{}" this\n'
                "indicates that wallpyper has already run, would\n"
                "you like to overwrite this directory?\n"
                "(y)es or (n)o".format(os.path.curdir)
            )
            == "y"
        ):
            pass
        elif os.path.curdir == "sorted":
            os.chdir("..")
            if os.path.isdir("sorted"):
                pass
                # os.removedirs('')


#        else:
#            pass
#    else:
#        if (
#            input(
#                "there is already a directory named \"sorted\" would you\n"
#               "like to make a new one, (y)es or (n)o to overwrite.\n"
#               "Warning! this will erase all content in the directory\n"
#            )
#            == "y"
#        ):
#            os.mkdir("sorted")

@jit(nopython=True)
def get_dominant_colors(filename, NUM_CLUSTERS):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # print ('reading image')
    try:
        input_image = Image.open(filename)
        input_image = input_image.resize(
            (150, 150)
        )  # optional, to reduce time
        image_array = np.asarray(input_image)  # convert image to array
        shape = image_array.shape
        # reshape array to merge color bands
        if len(shape) > 2:
            image_array = image_array.reshape(
                scipy.product(shape[:2]), shape[2]
            )

        # get clusters
        # print ('finding clusters')
        codes, _ = scipy.cluster.vq.kmeans(
            image_array.astype(float), NUM_CLUSTERS
        )
        # print( 'cluster centres:\n', codes)

        # vector quatisation
        vecs, _ = scipy.cluster.vq.vq(image_array, codes)  # assign codes

        # find most frequent
        counts, _ = scipy.histogram(vecs, len(codes))  # count occurrences
        index_max = scipy.argmax(counts)
        peak = codes[index_max]
        color = []
        for c in peak:
            color.append(int(c))
        rgb_color = color
        hex_color = "%02x%02x%02x" % (color[0], color[1], color[2])
        decimal_color = int(hex_color, 16)
        return hex_color, rgb_color, decimal_color
    except:
        print(
            "There was an error reading the file {} continuing with next file...".format(
                filename
            )
        )
        pass


@jit(nopython=True)
def sort_images(files_list, NUM_CLUSTERS):
    check_category_directories()

    i = 0
    for file in files_list:
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        i += 1
        print("-" * 80)
        print("processing image {} of {}...".format(i, len(files)))
        print("-" * 80)
        dominant_hex, dominant_rgb, dominant_decimal = get_dominant_colors(
            file, NUM_CLUSTERS
        )

        filename, file_extension = os.path.splitext(file)
        try:
            new_filename = "{}{}".format(dominant_hex, file_extension)
            os.copy(file, new_filename)
        except FileExistsError:
            new_filename = "{}{}{}".format(dominant_hex, i, file_extension)
            os.copy(file, new_filename)

        # comparison variables
        percent_range = 0.2
        pastel_limit = 180
        r = dominant_rgb[0]
        g = dominant_rgb[1]
        b = dominant_rgb[2]

        # greyscale
        if r == g == b:
            shutil.move(new_filename, "black and white")

        # pastel
        elif r >= pastel_limit and g >= pastel_limit and b >= pastel_limit:
            shutil.move(new_filename, "pastel")

        # blue more than red but less than green (green to cyan)
        elif b > r and b < g:
            shutil.move(new_filename, "cyan")

        # blue more than green but less than red (red to magenta)
        elif b > g and b < r:
            shutil.move(new_filename, "magenta")

        # green more than red but less than blue (blue to cyan)
        elif g > r and g < b:
            shutil.move(new_filename, "cyan")

        # green more than blue but less than  red (red to yellow)
        elif g > b and g < r:
            shutil.move(new_filename, "yellow")

        # red more than green but less than blue (blue to magenta)
        elif r > g and r < b:
            shutil.move(new_filename, "magenta")

        # red more than blue but less than green (green to yellow)
        elif r > b and r < g:
            shutil.move(new_filename, "yellow")

        # mostly red
        elif r > (g - int(g * percent_range)) and r > (
            b - int(b * percent_range)
        ):
            shutil.move(new_filename, "red")

        # mostly green (green more than red and blue)
        elif g > (r - int(r * percent_range)) and g > (
            b - int(b * percent_range)
        ):
            shutil.move(new_filename, "green")

        # mostly blue (blue more than green and red)
        elif b > (r - int(r * percent_range)) and b > (
            g - int(g * percent_range)
        ):
            shutil.move(new_filename, "blue")

        # dark
        elif r <= 40 and g <= 40 and b <= 40:
            shutil.move(new_filename, "dark")

        else:
            shutil.move(new_filename, "other")


if __name__ == "__main__":
    NUM_CLUSTERS = 2
    check_category_directories()
    path_to_images = os.path.curdir
    files = next(os.walk(path_to_images))[2]
    sort_images(files, NUM_CLUSTERS)
