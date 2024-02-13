# A class to process the output of export_detections.groovy and create label txt files
# for each of the tiles created from export_image_tiles.

import os
from pathlib import Path


class Label:
    class_to_idx = {
        'TA': 0,
        'CB': 1,
        'NFT': 2,
        'tau_fragments': 3,
        'Others': 4,
        'non_tau': 5
    }

    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.w = 0
        self.h = 0
        self.class_idx = -1

    def get_label_info(self, label: str):
        class_name, roi = label.strip().split(':')
        class_name = class_name.strip('[] ')
        if class_name in Label.class_to_idx:
            self.class_idx = Label.class_to_idx[class_name]
        else:
            return

        obj_info = roi[roi.find('('):].strip('()').split(',')
        self.x0 = int(obj_info[0])
        self.y0 = int(obj_info[1])
        self.w = int(obj_info[2])
        self.h = int(obj_info[3])


class LabelPreparer:
    def __init__(self, slide_id: str):
        """
        :param slide_id: e.g. '747316'
        """
        self.slide_id = slide_id

    def remove_unlabelled_objects(self: str, training_dir_name: str):
        """
        :param training_dir_name: Name of the training directory to be used
        :return:
        """
        detections_file = os.path.join('..', training_dir_name, 'anns', self.slide_id,
                                       f"{self.slide_id}_detections_all.txt")

        with open(detections_file, 'r') as detections:
            output_path = os.path.join('..', training_dir_name, 'anns', self.slide_id,
                                       f"{self.slide_id}_detections.txt")

            with open(output_path, 'w') as filtered_detections:
                for line in detections:
                    object_label = line.split(':')[0]
                    if object_label != "[Unlabelled] ":
                        filtered_detections.write(line)

    def separate_labels_by_tile(self, training_dir_name: str):
        # todo: maybe first check that the anns dir is empty to save work

        img_dir = os.path.join('..', training_dir_name, 'imgs', self.slide_id)
        ann_dir = os.path.join('..', training_dir_name, 'anns')
        out_dir = os.path.join('..', training_dir_name, 'anns', self.slide_id)

        all_anns_file = os.path.join(ann_dir, f"{self.slide_id}_detections.txt")

        for tile in os.listdir(img_dir):
            filename = Path(tile).stem

            # process filename to get tile bounds (a lot of hard coded values)
            tile_info = filename.split(',')
            tile_x0 = int(tile_info[1][2:])
            tile_y0 = int(tile_info[2][2:])
            tile_w = int(tile_info[3][2:])
            tile_h = int(tile_info[4][2:-1])

            with open(all_anns_file, 'r') as all_anns:
                all_anns.readline()  # skip first line

                out_anns_file = os.path.join(out_dir, f"{filename}.txt")

                with open(out_anns_file, 'w') as label_f:
                    for obj in all_anns:
                        # process the line to see if the detection is in this tile
                        label = Label()
                        label.get_label_info(obj)

                        # check bounds
                        if label.x0 >= tile_x0 and (label.x0 + label.w) < (tile_x0 + tile_w) and \
                                label.y0 >= tile_y0 and (label.y0 + label.h) < (tile_y0 + tile_h):

                            x_centre = (label.x0 + label.w/2 - tile_x0) / tile_w
                            y_centre = (label.y0 + label.h/2 - tile_y0) / tile_h

                            norm_width = label.w / tile_w
                            norm_height = label.h / tile_h

                            label_yolo = f"{label.class_idx} {x_centre} {y_centre} {norm_width} {norm_height}\n"

                            label_f.write(label_yolo)


    def delete_files_with_no_labels(self, training_dir_name: str):
        img_dir = os.path.join('..', training_dir_name, 'imgs', self.slide_id)
        ann_dir = os.path.join('..', training_dir_name, 'anns', self.slide_id)

        for tile in os.listdir(img_dir):
            filename = Path(tile).stem
            anns_file = os.path.join(ann_dir, f"{filename}.txt")

            if os.path.getsize(anns_file) == 0:
                os.remove(anns_file)
                # os.remove(tile)  # todo: do we risk this?


label_preparer = LabelPreparer('747316')
# label_preparer.remove_unlabelled_objects('small_training')
label_preparer.separate_labels_by_tile('small_training')
label_preparer.delete_files_with_no_labels('small_training')
