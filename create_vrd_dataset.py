import os
import urllib
import zipfile
import json
import random

def get_zip(url, zip_path, unzip_path):
    if not os.path.isfile(zip_path):
        urllib.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path) as zip_ref:
            zip_ref.extractall(unzip_path)

def get_dataset(data_dir):
    dataset_zip_path = os.path.join(data_dir, "json_dataset.zip")
    dataset_url = "http://cs.stanford.edu/people/ranjaykrishna/vrd/json_dataset.zip"
    get_zip(dataset_url, dataset_zip_path, data_dir)

    images_zip_path = os.path.join(data_dir, "sg_dataset.zip")
    images_url = "http://imagenet.stanford.edu/internal/jcjohns/scene_graphs/sg_dataset.zip"
    get_zip(images_url, images_zip_path, data_dir)

def create_tbox_json(data_dir):
    images_dir = os.path.join("sg_dataset", "sg_train_images")
    annotations_file = os.path.join(data_dir, "annotations_train.json")

    with open(annotations_file) as f:
        images_info = json.load(f)

    tbox_json = []
    for filename, image_info in images_info.items():
        rects = []
        subject_info = [pair["subject"] for pair in image_info]
        object_info = [pair["object"] for pair in image_info]
        for box_info in subject_info + object_info:
            ymin, ymax, xmin, xmax = box_info["bbox"]
            rects.append({
                "x1": xmin,
                "x2": xmax,
                "y1": ymin,
                "y2": ymax
            })

        image_json = {"image_path": os.path.join(images_dir, filename), "rects": rects}
        tbox_json.append(image_json)

    random.shuffle(tbox_json)
    split_idx = int(len(tbox_json) * 0.9)
    tbox_json_train = tbox_json[:split_idx]
    tbox_json_test = tbox_json[split_idx:]

    with open(os.path.join(data_dir, "train_boxes.json"), "w+") as f:
        json.dump(tbox_json_train, f)
    with open(os.path.join(data_dir, "val_boxes.json"), "w+") as f:
        json.dump(tbox_json_test, f)

if __name__ == "__main__":
    data_dir = "data/vrd"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    get_dataset(data_dir)
    create_tbox_json(data_dir)
