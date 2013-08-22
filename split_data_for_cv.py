#!/usr/local/bin/python3

""" Splits libsvm training data for cross validation.  The input should be
    raw training data (with real excess returns as labels instead of +/-1),
    and the output files will be compatible with libsvm.

    The way we split data is to sort all entries by date and then by ticker
    name, and split them into k equal segments.  For fold i, the training data
    will come from segments 1,...,i-1,i+1,...k, and the testing data will come
    from segment i.  This way there is little overlap in time between training
    and testing data, and the prediction will be (in theory) more difficult.
"""

import argparse
import logging
import utils

def close_all(fps):
  for fp in fps: fp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_path', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--folds', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)
  folds = int(args.folds)
  assert folds > 1

  with open(args.input_path, 'r') as fp:
    lines = fp.read().splitlines()
  # Swap date and ticker in place.
  item_count = -1
  for i in range(len(lines)):
    items = lines[i].split(' ')
    if item_count < 0: item_count = len(items)
    else: assert item_count == len(items)
    items[0], items[1] = items[1], items[0]
    lines[i] = ' '.join(items)
  # This will sort lines by entry and then ticker.
  lines.sort()

  # Prepare all the file handlers.  We are going to write to folds * 4 files,
  # with each fold a training data file, a training index file, a testing
  # data file, and a testing index file.
  train_data_fps, train_index_fps = [], []
  test_data_fps, test_index_fps = [], []
  for i in range(folds):
    train_data_fps.append(open('%s/train_data_%d' % (args.output_dir, i), 'w'))
    train_index_fps.append(open('%s/train_index_%d' % (args.output_dir, i),
                                'w'))
    test_data_fps.append(open('%s/test_data_%d' % (args.output_dir, i), 'w'))
    test_index_fps.append(open('%s/test_index_%d' % (args.output_dir, i), 'w'))
  # Sanity checks.
  assert len(train_data_fps) == folds
  assert len(train_index_fps) == folds
  assert len(test_data_fps) == folds
  assert len(test_index_fps) == folds

  segment = int(len(lines) / folds)
  for i in range(folds):
    logging.info('Writing fold %d' % (i+1))
    start = segment * i
    end = start + segment
    if i == folds - 1: end = len(lines)
    for j in range(start, end):
      items = lines[j].split(' ')
      # Write label, features to data files and date, ticker to index files.
      assert len(items) > 3
      data = '%s %s' % (utils.make_label(float(items[2]), False),
                        ' '.join(items[3:]))
      index = ' '.join(items[:2])
      for k in range(folds):
        if i != k:
          print(data, file=train_data_fps[k])
          print(index, file=train_index_fps[k])
        else:
          print(data, file=test_data_fps[k])
          print(index, file=test_index_fps[k])

  # Close all file handlers.
  close_all(train_data_fps)
  close_all(train_index_fps)
  close_all(test_data_fps)
  close_all(test_index_fps)

if __name__ == '__main__':
  main()

