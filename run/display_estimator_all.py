import os, sys
import argparse
import numpy as np
import gzip

# image processing
from PIL import Image
import cv2
from ipfml import utils
from ipfml.processing import transform, segmentation

import matplotlib.pyplot as plt

# module imports
from estimators import estimate, estimators_list

figures_output = 'data/figs'

def write_progress(progress):
    barWidth = 180

    output_str = "["
    pos = barWidth * progress
    for i in range(barWidth):
        if i < pos:
           output_str = output_str + "="
        elif i == pos:
           output_str = output_str + ">"
        else:
            output_str = output_str + " "

    output_str = output_str + "] " + str(int(progress * 100.0)) + " %\r"
    print(output_str)
    sys.stdout.write("\033[F")

def main():

    parser = argparse.ArgumentParser(description="Check complexity of each zone of scene using estimator during rendering")

    parser.add_argument('--folder', type=str, help='folder where scenes with png scene file are stored')
    parser.add_argument('--estimator', type=str, help='metric to use to compare', choices=estimators_list)
    parser.add_argument('--ylim', type=str, help='0,100 : ylim expected', default='')
    parser.add_argument('--output', type=str, help='output folder name', required=True)

    args = parser.parse_args()

    p_folder = args.folder
    p_estimator  = args.estimator
    p_y_lim = args.ylim
    p_output = args.output

    folders = [ f for f in os.listdir(p_folder) if 'min_max' not in f ]

    for scene in sorted(folders):

        zones = []
        zones_indices = np.arange(16)

        for _ in zones_indices:
            zones.append([])
            
        print('Start extracting', p_estimator, 'for', scene)
        scene_folder = os.path.join(p_folder, scene)

        # get all images and extract estimator for each blocks
        images = sorted([ i for i in os.listdir(scene_folder) if '.png' in i ])
        n_images = float(len(images))

        for i, img_name in enumerate(images):
            img_path = os.path.join(scene_folder, img_name)

            img_arr = np.array(Image.open(img_path))

            blocks = segmentation.divide_in_blocks(img_arr, (200, 200))
            
            for index, b in enumerate(blocks):
                zones[index].append(estimate(p_estimator, b))

            write_progress((i + 1) / n_images)

        
        # display each block stats
        plt.figure(figsize=(25, 20))
        plt.rc('xtick', labelsize=22)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=22)    # fontsize of the tick labels

        for i, zone in enumerate(zones):
            plt.plot(zone, linewidth=3, label='zone ' + str(i))

        plt.title('Estimator evolution on zones for ' + scene, fontsize=30)
        plt.legend(fontsize=20)
        plt.xlabel('Number of images', fontsize=28)
        plt.ylabel(p_estimator + ' evolution during rendering', fontsize=28)
        
        if len(p_y_lim) > 0:
            p_x, p_y = list(map(int, p_y_lim.split(',')))
            plt.ylim((p_x, p_y))
        
        output_folder = os.path.join(figures_output, p_output)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        plt.savefig(os.path.join(output_folder, p_estimator + '_' + scene + '.png')) #, transparent=True)
        print()


if __name__ == "__main__":
    main()