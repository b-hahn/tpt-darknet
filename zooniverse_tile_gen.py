import os
import math
import csv
from os import path
import numpy as np
from imageio import imread, imsave


def main(beach_name,
         beach_name_manifest,
         geo_area_manifest,
         date_survey_manifest,
         survey_id,
         source_img_path,
         output_dir="zooniverse_tiles",
         desired_output_width=90,
         desired_output_height=67,
         overlap=0.1,
         attribution="Peter Kohler"
         ):
    tile_id = survey_id * 100000

    source_img_path = path.abspath(path.expanduser(source_img_path))
    output_dir = path.abspath(path.expanduser(output_dir))
    save_path = path.join(output_dir, beach_name)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    print('Saving images to', save_path, '.')

    # prepare manifest file
    # QUESTION: should the image name be an absolute or relative path?
    manifest_line = [['subject_id', 'image_name1', 'attribution', 'beach', 'region', 'date']]

    # loop through all .JPG files in directory.
    images = [os.path.join(source_img_path, f) for f in os.listdir(source_img_path) if
              (os.path.isfile(os.path.join(source_img_path, f)) and f.lower().endswith('.jpg'))]

    # loop through all images in directory
    for input_file_name in images:
        print()
        print('Processing file {}'.format(input_file_name))

        # load image
        img = imread(input_file_name)

        # calculate number of output image tiles
        input_height, input_width = img.shape[0:2]
        print(' Image dimensions: w =', input_height, ', h =', input_width)

        horizontal_tiles = round((input_width - desired_output_width) / (
                desired_output_width * (1 - overlap)))  # round down since we don't want to crop any parts of
        # the image or lose any accuracy.
        vertical_tiles = round((input_height - desired_output_height) / (desired_output_height * (1 - overlap)))

        # calculate the amount the overlap needs to be increased/ decreased to enable about the right number of tiles without going
        # beyond the image boundaries
        tile_width_exact_fit = (input_width - desired_output_width) / horizontal_tiles
        tile_height_exact_fit = (input_height - desired_output_height) / vertical_tiles

        overlap_adjusted_horizontal = (desired_output_width - tile_width_exact_fit) / desired_output_width
        overlap_adjusted_vertical = (desired_output_height - tile_height_exact_fit) / desired_output_height

        output_width = desired_output_width  # input_width / horizontal_tiles
        output_height = desired_output_height  # input_height / vertical_tiles

        print(' Creating', horizontal_tiles + 1, '*', vertical_tiles + 1, '=',
              (horizontal_tiles + 1) * (vertical_tiles + 1),
              'output image tiles.')
        print(' Tile width:', output_width)
        print(' Tile hight:', output_height)
        print(' Horizontal Overlap:', '{0:.2f}'.format(overlap_adjusted_horizontal * 100), '%.')
        print(' Vertical Overlap:', '{0:.2f}'.format(overlap_adjusted_vertical * 100), '%.')

        # loop through original image and save each tile
        # The + 1 is due to the python range not including the last element -
        # we want to see where the that tile starts as well, though
        for i in range(0, int(horizontal_tiles + 1)):
            for j in range(0, int(vertical_tiles + 1)):
                # calculate tile begin in x and y direction
                tile_begin_x = math.floor(i * output_width - i * output_width * overlap_adjusted_horizontal)
                tile_end_x = math.floor(tile_begin_x + output_width)
                tile_begin_y = math.floor(j * output_height - j * output_height * overlap_adjusted_vertical)
                tile_end_y = math.floor(tile_begin_y + output_height)

                # draw the lines
                # cv2.line(img, (tile_begin_x, 0), (tile_begin_x, input_height), (0, 0, 255), 10)
                # cv2.line(img, (0, tile_begin_y), (input_width, tile_begin_y), (0, 0, 255), 10)

                tile = img[int(tile_begin_y):int(tile_end_y), int(tile_begin_x):int(tile_end_x)]

                fn = "{}_{}_tile_{}_{}.jpg".format(beach_name, path.splitext(path.basename(input_file_name))[0], i, j)
                output_file_name = path.join(save_path, fn)

                print('   Tile ({}, {}) x: ({}, {}), y: ({}, {}) -> {}'.format(i, j, tile_begin_x, tile_end_x,
                                                                               tile_begin_y, tile_end_y,
                                                                               output_file_name))
                imsave(output_file_name, tile)

                # write line to .csv file containing the zooniverse manifest, as described on their website
                tile_id += 1
                manifest_line.append([str(tile_id),
                                      path.basename(output_file_name),
                                      attribution,
                                      beach_name_manifest,
                                      geo_area_manifest,
                                      date_survey_manifest])

    with open(path.join(save_path, 'manifest.csv'), 'w') as manifest_file:
        writer = csv.writer(manifest_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(manifest_line)


if __name__ == "__main__":
    beach_name = "islandbeachstatepark"
    beach_name_manifest = "Island Beach State Park"
    geo_area_manifest = "New Jersey"
    date_survey_manifest = "17/11/2017"
    survey_id = 25
    source_img_path = 'data/statepark/'  # set to '.' to read all images in current directory
    source_img_path = "~/code/traffic-light-utils/data/toytest/"

    main(beach_name,
         beach_name_manifest,
         geo_area_manifest,
         date_survey_manifest,
         survey_id,
         source_img_path,
         attribution="Peter Kohler",
         output_dir="zooniverse_tiles")
