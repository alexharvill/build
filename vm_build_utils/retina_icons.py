#!/usr/bin/env python
# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
'''
build icon png files of various sizes in XCode retina icon format
'''
import os
import json
import logging
import argparse
import subprocess

try:
  import cv2
except ImportError:
  logging.warning('cannot import cv2')


def default_iconset_contents_json():
  'a reasonable Contents.json default - must remove shape items before saving'
  return {
      'images': [
          {
              'filename': '20@2x.png',
              'idiom': 'iphone',
              'scale': '2x',
              'shape': [40, 40],
              'size': '20x20'
          },
          {
              'filename': '20@3x.png',
              'idiom': 'iphone',
              'scale': '3x',
              'shape': [60, 60],
              'size': '20x20'
          },
          {
              'filename': '20.png',
              'idiom': 'ipad',
              'scale': '1x',
              'shape': [20, 20],
              'size': '20x20'
          },
          {
              'filename': '20@2x.png',
              'idiom': 'ipad',
              'scale': '2x',
              'shape': [40, 40],
              'size': '20x20'
          },
          {
              'filename': '29@2x.png',
              'idiom': 'iphone',
              'scale': '2x',
              'shape': [58, 58],
              'size': '29x29'
          },
          {
              'filename': '29@3x.png',
              'idiom': 'iphone',
              'scale': '3x',
              'shape': [87, 87],
              'size': '29x29'
          },
          {
              'filename': '40@2x.png',
              'idiom': 'iphone',
              'scale': '2x',
              'shape': [80, 80],
              'size': '40x40'
          },
          {
              'filename': '40@3x.png',
              'idiom': 'iphone',
              'scale': '3x',
              'shape': [120, 120],
              'size': '40x40'
          },
          {
              'filename': '60@2x.png',
              'idiom': 'iphone',
              'scale': '2x',
              'shape': [120, 120],
              'size': '60x60'
          },
          {
              'filename': '60@3x.png',
              'idiom': 'iphone',
              'scale': '3x',
              'shape': [180, 180],
              'size': '60x60'
          },
          {
              'filename': '29.png',
              'idiom': 'ipad',
              'scale': '1x',
              'shape': [29, 29],
              'size': '29x29'
          },
          {
              'filename': '29@2x.png',
              'idiom': 'ipad',
              'scale': '2x',
              'shape': [58, 58],
              'size': '29x29'
          },
          {
              'filename': '40.png',
              'idiom': 'ipad',
              'scale': '1x',
              'shape': [40, 40],
              'size': '40x40'
          },
          {
              'filename': '40@2x.png',
              'idiom': 'ipad',
              'scale': '2x',
              'shape': [80, 80],
              'size': '40x40'
          },
          {
              'filename': '76.png',
              'idiom': 'ipad',
              'scale': '1x',
              'shape': [76, 76],
              'size': '76x76'
          },
          {
              'filename': '76@2x.png',
              'idiom': 'ipad',
              'scale': '2x',
              'shape': [152, 152],
              'size': '76x76'
          },
          {
              'filename': '83.5@2x.png',
              'idiom': 'ipad',
              'scale': '2x',
              'shape': [167, 167],
              'size': '83.5x83.5'
          },
          {
              'filename': '1024.png',
              'idiom': 'ios-marketing',
              'scale': '1x',
              'shape': [1024, 1024],
              'size': '1024x1024'
          },
      ],
      'info': {
          'author': 'retina_icons.py',
          'version': 1
      }
  }


def default_imageset_contents_json():
  'universal Contents.json default - must remove shape items before saving'
  return {
      "images": [{
          "filename": ".png",
          "idiom": "universal",
          "scale": "1x",
          "shape": [240, 240]
      }, {
          "filename": "@2x.png",
          "idiom": "universal",
          "scale": "2x",
          "shape": [480, 480]
      }, {
          "filename": "@3x.png",
          "idiom": "universal",
          "scale": "3x",
          "shape": [720, 720]
      }],
      "info": {
          "author": "retina_icons.py",
          "version": 1
      }
  }


def default_launchimage_contents_json():
  'universal Contents.json default - must remove shape items before saving'
  return {
  "images" : [
    {
      "orientation" : "portrait",
      "idiom" : "iphone",
      "extent" : "full-screen",
      "filename" : "1242x2688@3x.png",
      "minimum-system-version" : "12.0",
      "subtype" : "2688h",
      "scale" : "3x",
      "shape": [2688, 1242]
    },
    {
      "orientation" : "portrait",
      "idiom" : "iphone",
      "extent" : "full-screen",
      "filename" : "828x1792@2x.png",
      "minimum-system-version" : "12.0",
      "subtype" : "1792h",
      "scale" : "2x",
      "shape": [1792, 828]
    },
    {
      "extent" : "full-screen",
      "idiom" : "iphone",
      "subtype" : "2436h",
      "filename" : "1125x2436@3x.png",
      "minimum-system-version" : "11.0",
      "orientation" : "portrait",
      "scale" : "3x",
      "shape": [2436, 1125]
    },
    {
      "orientation" : "portrait",
      "idiom" : "iphone",
      "extent" : "full-screen",
      "minimum-system-version" : "8.0",
      "subtype" : "736h",
      "filename" : "1242x2208@3x.png",
      "scale" : "3x",
      "shape": [2208, 1242]
    },
    {
      "orientation" : "portrait",
      "idiom" : "iphone",
      "extent" : "full-screen",
      "filename" : "750x1334@2x.png",
      "minimum-system-version" : "8.0",
      "subtype" : "667h",
      "scale" : "2x",
      "shape": [1334, 750]
    }
  ],
  "info" : {
    "version" : 1,
    "author" : "retina_icons.py"
  }
}


def build_parser():
  'get a parser for this command'
  parser = argparse.ArgumentParser(description=__doc__)

  parser.add_argument(
      '-v',
      '--verbose',
      help='more debugging info',
      action='store_true',
  )

  parser.add_argument(
      '--get-outputs',
      help='print list of output files',
      action='store_true',
  )

  parser.add_argument(
      '--asset-build-dir',
      help='path to parnet build xcasset directory',
  )

  parser.add_argument(
      '--iconset',
      help='name of the iconset to generate',
  )

  parser.add_argument(
      '--src',
      help='path to src image',
      required=True,
  )

  parser.add_argument(
      '--build-info',
      help='just memorize information for incoming icons',
      action='store_true',
  )

  parser.add_argument(
      '--interpolation',
      help='weights to use for resizing',
      default='INTER_AREA',
      choices=[
          'INTER_AREA',
          'INTER_BITS',
          'INTER_BITS2',
          'INTER_CUBIC',
          'INTER_LANCZOS4',
          'INTER_LINEAR',
          'INTER_LINEAR_EXACT',
          'INTER_MAX',
          'INTER_NEAREST',
          'INTER_TAB_SIZE',
          'INTER_TAB_SIZE2',
      ],
  )

  return parser


def read_rgb8_image_cv2(path):
  'read 8bit rgb image using opencv'
  img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
  return img


def write_rgb8_image_cv2(img, path):
  'write 8bit rgb image using opencv'
  cv2.imwrite(path, img)


def build_info(dir_path):
  'read a specific Contents.json and summarize for default_contents_json()'

  json_path = os.path.join(dir_path, 'Contents.json')

  with open(json_path) as fd:
    contents = json.load(fd)

  image_info = []
  for info in contents['images']:
    icon_path = os.path.join(dir_path, info['filename'])

    tmp_img = read_rgb8_image_cv2(icon_path)

    info['filename'] = info['filename'].rsplit('-', 1)[-1]
    info['shape'] = list(tmp_img.shape)[:-1]
    image_info.append(info)

  output = dict(
      images=image_info,
      info=dict(version=1, author='retina_icons.py'),
  )
  print(json.dumps(
      output,
      indent=2,
      sort_keys=True,
  ))


def main():
  'read icons, save out as a directory structure of apple style icons'
  parser = build_parser()
  args = parser.parse_args()

  if not args.verbose:
    logging.getLogger('').setLevel(logging.WARNING)

  build = not args.get_outputs

  if args.build_info:
    build_info(args.src)
  else:
    interpolation = getattr(cv2, args.interpolation)

    output_icon_path = os.path.join(args.asset_build_dir, args.iconset)

    icon_name = os.path.splitext(os.path.basename(args.src))[0]

    if args.iconset.endswith('imageset'):
      contents = default_imageset_contents_json()
    elif args.iconset.endswith('launchimage'):
      contents = default_launchimage_contents_json()
    elif args.iconset.endswith('appiconset'):
      contents = default_iconset_contents_json()
    else:
      raise ValueError(
          '%s does not end with .imageset | .launchimage | .appiconset')

    src_img = None
    if build:
      mkdir_cmd = ['mkdir', '-p', output_icon_path]
      logging.info(' '.join(mkdir_cmd))
      subprocess.check_call(mkdir_cmd)

      src_img = read_rgb8_image_cv2(args.src)

    contents_path = os.path.join(output_icon_path, 'Contents.json')
    output_paths = [(-1, contents_path)]

    for info in contents['images']:
      output_name = icon_name + '-' + info['filename']
      output_path = os.path.join(output_icon_path, output_name)
      output_paths.append((info['shape'][1], output_path))

      info['filename'] = output_name

      if build:
        target_h, target_w = info.pop('shape')

        src_h, src_w, _ = src_img.shape

        print('%s -> %s' % ((src_h, src_w), (target_h, target_w)))

        if (src_h, src_w) == (target_h, target_w):
          dst_img = src_img

        else:

          scale = float(min(target_h, target_w)) / float(max(src_h, src_w))

          intermediate_w = int(scale * src_w)
          intermediate_h = int(scale * src_h)

          dst_img = cv2.resize(
              src_img,
              dsize=(intermediate_w, intermediate_h),
              interpolation=interpolation,
          )

          t_pad = int((target_h - intermediate_h) / 2)
          b_pad = target_h - intermediate_h - t_pad

          l_pad = int((target_w - intermediate_w) / 2)
          r_pad = target_w - intermediate_w - l_pad

          dst_img = cv2.copyMakeBorder(
              dst_img,
              top=t_pad,
              bottom=b_pad,
              left=l_pad,
              right=r_pad,
              borderType=cv2.BORDER_CONSTANT,
              value=[255, 255, 255, 255],
          )

          final_h, final_w, _ = dst_img.shape
          # print( 'final h', final_h, target_h)
          # print( 'final w', final_w, target_w)
          assert final_h == target_h, 'h mismatch'
          assert final_w == target_w, 'h mismatch'

        write_rgb8_image_cv2(dst_img, output_path)

        logging.info('output image: %s', output_path)

    if build:
      logging.info('output json: %s', contents_path)
      with open(contents_path, 'w') as fd:
        json.dump(contents, fd, indent=2, sort_keys=True)

  if args.get_outputs:
    outputs = []
    for _, path in sorted(output_paths):
      outputs.append(path)
    print('\n'.join(outputs))


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  main()
