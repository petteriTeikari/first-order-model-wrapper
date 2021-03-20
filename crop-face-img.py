import face_alignment
import skimage.io
import numpy
from argparse import ArgumentParser
from skimage import img_as_ubyte
from skimage.transform import resize
from tqdm import tqdm
import os
import imageio
import numpy as np
import warnings

import time
from datetime import timedelta

warnings.filterwarnings("ignore")

def extract_bbox(frame, fa):
    if max(frame.shape[0], frame.shape[1]) > 640:
        scale_factor = max(frame.shape[0], frame.shape[1]) / 640.0
        frame = resize(frame, (int(frame.shape[0] / scale_factor), int(frame.shape[1] / scale_factor)))
        frame = img_as_ubyte(frame)
    else:
        scale_factor = 1
    frame = frame[..., :3]
    bboxes = fa.face_detector.detect_from_image(frame[..., ::-1])
    if len(bboxes) == 0:
        return []

    scaled_bboxes = np.array(bboxes)[:, :-1] * scale_factor

    return scaled_bboxes, frame


def crop_to_box(frame, scaled_bbox, increase_area=0.1):

    frame_shape = frame.shape

    scaled_bbox= scaled_bbox[0]
    # print(scaled_bbox)
    left, top, right, bot = scaled_bbox[0], scaled_bbox[1], scaled_bbox[2], scaled_bbox[3]
    width = right - left
    height = bot - top

    # Computing aspect preserving bbox
    width_increase = max(increase_area, ((1 + 2 * increase_area) * height - width) / (2 * width))
    height_increase = max(increase_area, ((1 + 2 * increase_area) * width - height) / (2 * height))

    left = int(left - width_increase * width)
    top = int(top - height_increase * height)
    right = int(right + width_increase * width)
    bot = int(bot + height_increase * height)

    top, bot, left, right = max(0, top), min(bot, frame_shape[0]), max(0, left), min(right, frame_shape[1])
    h, w = bot - top, right - left

    frame_crop = frame[left:right, top:bot]

    return frame_crop, top, bot, left, right

def process_img(args):

    device = 'cpu' if args.cpu else 'cuda'
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device=device)

    img_fpath = args.inp
    # img_fpath = '/home/petteri/Dropbox/manuscriptDrafts/deepArt/ECCV/images/pt_20201127_ugneShoot_194_medium.jpg'
    frame = skimage.io.imread(img_fpath)

    img_shape = frame.shape
    frame_shape = frame.shape
    scaled_bbox, frame = extract_bbox(frame, fa)

    frame_crop, top, bot, left, right = crop_to_box(frame, scaled_bbox)
    # print(frame_crop.shape)

    return frame_crop

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--image_shape", default=(256, 256), type=lambda x: tuple(map(int, x.split(','))),
                        help="Image shape")
    parser.add_argument("--increase", default=0.1, type=float, help='Increase bbox by this amount')
    parser.add_argument("--iou_with_initial", type=float, default=0.25, help="The minimal allowed iou with inital bbox")
    parser.add_argument("--inp", required=True, help='Input image')
    parser.add_argument("--cpu", dest="cpu", action="store_true", help="cpu mode.")

    args = parser.parse_args()

    start_time = time.monotonic()
    frame_crop = process_img(args)
    end_time = time.monotonic()

    fpath = args.inp
    out_path = os.path.split(fpath)[0]
    fname = os.path.split(fpath)[1]
    split_fname = fname.split('.')
    ext = split_fname[1]
    output_fname = split_fname[0]
    output_fname += '_crop.' + ext
    output_fpath = os.path.join(out_path, output_fname)
    skimage.io.imsave(output_fpath, frame_crop)
    print('Image cropped in {}, and saved to {}'.format(timedelta(seconds=end_time - start_time),
                                                        output_fpath))