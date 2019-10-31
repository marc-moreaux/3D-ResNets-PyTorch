#!/usr/bin/python3
''' Use this code to convert directory of videos into directories of
directories of JPG.

Example:
    video_jpg.py /mp4/path /dst/path
    video_jpg.py /mp4/path /dst/path .avi
    video_jpg.py /dataset/path /dst/path .avi dataset
    video_jpg.py /dataset/path /dst/path .mp4 dataset
'''

from __future__ import print_function, division
import os
import sys
import subprocess


def video_to_jpgs(video_file_path, dst_directory_path):
    ''' Convert a video to jpgs '''
    cmd = 'ffmpeg -i {} -vf scale=-1:360 {}/image_%05d.jpg'.format(
        video_file_path, dst_directory_path)
    print(cmd)
    subprocess.call(cmd, shell=True)
    print('\n')


def dir_video_to_jpgs(dir_path, dst_dir_path, video_extention='.mp4'):
    ''' Converts directory of videos in directories of directories of jpgs '''
    if video_extention is None:
        video_extention = '.mp4'

    for file_name in os.listdir(dir_path):
        if video_extention not in file_name:
            continue
        name, ext = os.path.splitext(file_name)
        dst_directory_path = os.path.join(dst_dir_path, name)
        video_file_path = os.path.join(dir_path, file_name)

        # Maybe delete old jpgs
        try:
            if os.path.exists(dst_directory_path):
                if not os.path.exists(os.path.join(dst_directory_path,
                                                   'image_00001.jpg')):
                    subprocess.call('rm -r {}'.format(dst_directory_path),
                                    shell=True)
                    print('remove {}'.format(dst_directory_path))
                    os.mkdir(dst_directory_path)
                else:
                    continue
            else:
                os.mkdir(dst_directory_path)
        except:
            print(dst_directory_path)
            continue

        # Create new jpgs
        video_to_jpgs(video_file_path, dst_directory_path)


if __name__ == "__main__":
    # Get args
    dir_path = sys.argv[1]
    dst_dir_path = sys.argv[2]
    video_extention = sys.argv[3] if len(sys.argv) > 3 else '.mp4'
    dataset_mode = True if len(sys.argv) > 4 else False

    # Select dataset mode or single directory mode
    if not dataset_mode:
        dir_video_to_jpgs(dir_path, dst_dir_path, video_extention)
    else:
        # Loop classes
        for class_name in os.listdir(dir_path):
            class_path = os.path.join(dir_path, class_name)
            if not os.path.isdir(class_path):
                continue

            # Create jpg class dir
            dst_class_path = os.path.join(dst_dir_path, class_name)
            if not os.path.exists(dst_class_path):
                os.makedirs(dst_class_path)

            # Convert dir of videos to dir of dir of jpgs
            dir_video_to_jpgs(class_path, dst_class_path, video_extention)
