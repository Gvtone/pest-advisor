from sahi.utils.yolov8 import download_yolov8s_model

from sahi import AutoDetectionModel
from sahi.utils.cv import read_image
from sahi.utils.file import download_from_url
from sahi.predict import get_prediction, get_sliced_prediction, predict
from sahi.prediction import visualize_object_predictions
from numpy import asarray
import cv2
import os
import json
from datetime import datetime
import requests


def predict(img, weightPath):
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='yolov8',
        model_path=weightPath,
        confidence_threshold=0.5,
        device='cuda:0'
    )

    imageName = stripExtension(img)

    result = get_sliced_prediction(
        img,
        detection_model,
        slice_height=864,
        slice_width=864,
        overlap_height_ratio=0.7,
        overlap_width_ratio=0.7,
    )

    img = cv2.imread(img, cv2.IMREAD_UNCHANGED)
    img_converted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    numpydata = asarray(img_converted)
    visualize_object_predictions(
        numpydata,
        object_prediction_list=result.object_prediction_list,
        hide_labels=0,
        text_size=0.8,
        output_dir='./static/predictions/',
        file_name=imageName,
        export_format='png'
    )

    population = {}
    for prediction in result.object_prediction_list:
        population[prediction.category.name] = 0

    for prediction in result.object_prediction_list:
        population[prediction.category.name] += 1

    predictions_directory = "./static/predictions"
    os.makedirs(predictions_directory, exist_ok=True)

    json_file_path = os.path.join(predictions_directory, imageName)

    json_data = json.dumps(population, indent=4)
    with open(json_file_path + ".json", 'w') as json_file:
        json_file.write(json_data)

    return True


def fileDatetime(datetime_string):
    # Split the datetime string into date and time components
    date_str, time_str = datetime_string.split('_')

    # Convert date and time strings to datetime objects
    y, m, d = date_str.split('-')
    H, M = time_str.split('-')
    date_time_object = datetime(int(y), int(m), int(d), int(H), int(M))

    date_object = date_time_object.date()
    time_object = date_time_object.time()

    return date_object, time_object


def stripExtension(image_filename):
    # Use os.path.basename to get the file name from the path
    file_name = os.path.basename(image_filename)

    # Check if the file has a ".png" extension
    if file_name.lower().endswith(".png"):
        # Strip the ".png" extension
        stripped_filename = os.path.splitext(file_name)[0]
        return stripped_filename
    elif file_name.lower().endswith(".jpg"):
        stripped_filename = os.path.splitext(file_name)[0]
        return stripped_filename
    else:
        print("The provided path does not lead to a PNG/JPG image.")
        return None


def requestJSON(api_url):
    try:
        # Make a GET request to the API
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON data from the response
            json_data = response.json()

            return json_data
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        # Handle any exceptions that may occur during the request
        print(f"Error: {e}")
        return None


def latestFile(directory_path):
    try:
        # Get a list of filenames in the specified directory
        filenames = os.listdir(directory_path)

        for filename in filenames:
            return filename

    except FileNotFoundError:
        print(f"Directory not found: {directory_path}")
    except PermissionError:
        print(f"Permission error accessing: {directory_path}")


def deleteFiles(directory_path):
    try:
        # Get a list of all files in the specified directory
        all_files = [os.path.join(directory_path, f) for f in os.listdir(
            directory_path) if os.path.isfile(os.path.join(directory_path, f))]

        # If there are no files in the directory, print a message and return
        if not all_files:
            print(f"No files found in {directory_path}")
            return

        # Delete each file in the list
        for file_path in all_files:
            os.remove(file_path)
            print(f"Deleted: {file_path}")

        print(f"All files in {directory_path} have been deleted.")

    except FileNotFoundError:
        print(f"Directory not found: {directory_path}")
    except PermissionError:
        print(f"Permission error accessing: {directory_path}")
