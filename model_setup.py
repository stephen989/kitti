from video_processing import *

MODEL_URL = 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet50_coco_2018_01_28.tar.gz'

CLASS_LABELS = {1: "person", 2: "bicycle", 3: "car", 4: "motorcycle", 5: "airplane", 6: "bus", 7: "train", 8: "truck",
                9: "boat", 10: "traffic light", 11: "fire hydrant", 13: "stop sign", 14: "parking meter", 15: "bench",
                16: "bird", 17: "cat", 18: "dog", 19: "horse", 20: "sheep", 21: "cow", 22: "elephant", 23: "bear",
                24: "zebra", 25: "giraffe", 27: "backpack", 28: "umbrella", 31: "handbag", 32: "tie", 33: "suitcase",
                34: "frisbee", 35: "skis", 36: "snowboard", 37: "sports ball", 38: "kite", 39: "baseball bat",
                40: "baseball glove", 41: "skateboard", 42: "surfboard", 43: "tennis racket", 44: "bottle",
                46: "wine glass", 47: "cup", 48: "fork", 49: "knife", 50: "spoon", 51: "bowl", 52: "banana",
                53: "apple", 54: "sandwich", 55: "orange", 56: "broccoli", 57: "carrot", 58: "hot dog", 59: "pizza",
                60: "donut", 61: "cake", 62: "chair", 63: "couch", 64: "potted plant", 65: "bed", 67: "dining table",
                70: "toilet", 72: "tv", 73: "laptop", 74: "mouse", 75: "remote", 76: "keyboard", 77: "cell phone",
                78: "microwave", 79: "oven", 80: "toaster", 81: "sink", 82: "refrigerator", 84: "book", 85: "clock",
                86: "vase", 87: "scissors", 88: "teddy bear", 89: "hair drier", 90: "toothbrush"}

def fake_model():
    return None

def load_model():
    model_url = 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet50_coco_2018_01_28.tar.gz'
    base_url = os.path.dirname(model_url) + "/"
    model_file = os.path.basename(model_url)
    model_name = os.path.splitext(os.path.splitext(model_file)[0])[0]
    model_dir = tf.keras.utils.get_file(fname=model_name, origin=base_url + model_file, untar=True)
    model_dir = pathlib.Path(model_dir) / "saved_model"
    model = tf.saved_model.load(str(model_dir))
    model = model.signatures['serving_default']
    return model

def load_yolo(version='yolov5s'):
    import torch
    model = torch.hub.load('ultralytics/yolov5', version)
    return model, version, 'yolo'

def load_tensorflow(model_url = MODEL_URL):
    import tensorflow as tf
    base_url = os.path.dirname(model_url) + "/"
    model_file = os.path.basename(model_url)
    model_name = os.path.splitext(os.path.splitext(model_file)[0])[0]
    print(f"Loading/downloading {model_name}")
    model_dir = tf.keras.utils.get_file(fname=model_name,
                                        origin=base_url + model_file,
                                        untar=True)
    model_dir = pathlib.Path(model_dir) / "saved_model"
    model = tf.saved_model.load(str(model_dir))
    model = model.signatures['serving_default']
    model_type = "resnet50"
    print("Model loaded")
    return model, model_name, model_type

class Model:
    def __init__(self, load_fn):
        self.model, self.name, self.type = load_fn()

        self.call_function_mapping = {
            'resnet50': self.resnet_forward,
            'yolo': self.yolo_forward
        }

    def __call__(self, img):
        return self.call_function_mapping[self.type](img)

    def yolo_forward(self, img):
        results = self.model(img)  # batch of images
        results = results.pred[0].numpy()

        coords = results[:,:4]
        coords = coords.reshape(coords.shape[:-1] + (2, 2)).astype("int")
        coords = coords.tolist()
        prediction_scores = results[:, 4].round(3).tolist()
        prediction_classes = results[:, 5].astype("int").tolist()

        output_dict = {"detection_boxes": coords,
                       "detection_classes": prediction_classes,
                       "detection_scores": prediction_scores,
                       "num_detections": len(coords)}
        return output_dict

    def resnet_forward(self, img):
        if self.model is None:
            return {
                'detection_classes': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 8.0, 8.0, 33.0, 6.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 'detection_boxes': [
                    [0.15612861514091492, 0.4292111396789551, 0.2164933681488037, 0.47518032789230347],
                    [0.7057805061340332, 0.5771802663803101, 0.830472469329834, 0.6662591695785522],
                    [0.6096486449241638, 0.43104317784309387, 0.7558966279029846, 0.5065366625785828],
                    [0.5456079840660095, 0.5512152910232544, 0.6693922877311707, 0.6245009899139404],
                    [0.4947570860385895, 0.43675294518470764, 0.5917407870292664, 0.5014550685882568],
                    [0.1820029765367508, 0.5036328434944153, 0.24669967591762543, 0.5534780621528625],
                    [0.25916045904159546, 0.35074910521507263, 0.3438711166381836, 0.40468332171440125],
                    [0.8421770930290222, 0.5855169296264648, 0.9961211085319519, 0.6831520795822144],
                    [0.31730878353118896, 0.32999369502067566, 0.40956664085388184, 0.39205309748649597],
                    [0.3075726628303528, 0.5239355564117432, 0.465444952249527, 0.5870167016983032],
                    [0.3010830879211426, 0.5227512717247009, 0.47175922989845276, 0.5860163569450378],
                    [0.3555082678794861, 0.27816838026046753, 0.7346047163009644, 0.39062798023223877],
                    [0.12581518292427063, 0.16863855719566345, 0.9488135576248169, 0.8527395725250244],
                    [0.3640589714050293, 0.2795614004135132, 0.7338936924934387, 0.3891977071762085],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], 'num_detections': [14.0],
                'detection_scores': [0.9795929193496704, 0.9508070349693298, 0.9276410341262817, 0.9104766249656677,
                                     0.8870362043380737, 0.824179470539093, 0.7040495872497559, 0.6604017615318298,
                                     0.5824876427650452, 0.48015695810317993, 0.4105406105518341,
                                     0.39919009804725647, 0.362751305103302, 0.3524312376976013, 0.0, 0.0, 0.0, 0.0,
                                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                     0.0, 0.0]}
        input_tensor = tf.convert_to_tensor(img)
        input_tensor = input_tensor[tf.newaxis, ...]
        output_dict = self.model(input_tensor)
        n_detections = int(output_dict['num_detections'])
        for key in output_dict.keys():
            if key != "num_detections":
                output_dict[key] = output_dict[key].numpy().squeeze().tolist()[:n_detections]
        output_dict["num_detections"] = n_detections
        # scale coordinates to proper image scale
        height, width, _ = img.shape
        hwhw = np.array([height, width, height, width]).reshape(1, 4)
        boxes = np.array(output_dict['detection_boxes'])
        scaled_coords = np.array(hwhw * boxes).astype("int")
        scaled_coords = scaled_coords.reshape(scaled_coords.shape[:-1] + (2, 2))
        scaled_coords = scaled_coords[:, :, [1, 0]].tolist()
        output_dict["detection_boxes"] = scaled_coords
        return output_dict

def model_forward(model, img):
    if model is None:
        return {'detection_classes': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 8.0, 8.0, 33.0, 6.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 'detection_boxes': [[0.15612861514091492, 0.4292111396789551, 0.2164933681488037, 0.47518032789230347], [0.7057805061340332, 0.5771802663803101, 0.830472469329834, 0.6662591695785522], [0.6096486449241638, 0.43104317784309387, 0.7558966279029846, 0.5065366625785828], [0.5456079840660095, 0.5512152910232544, 0.6693922877311707, 0.6245009899139404], [0.4947570860385895, 0.43675294518470764, 0.5917407870292664, 0.5014550685882568], [0.1820029765367508, 0.5036328434944153, 0.24669967591762543, 0.5534780621528625], [0.25916045904159546, 0.35074910521507263, 0.3438711166381836, 0.40468332171440125], [0.8421770930290222, 0.5855169296264648, 0.9961211085319519, 0.6831520795822144], [0.31730878353118896, 0.32999369502067566, 0.40956664085388184, 0.39205309748649597], [0.3075726628303528, 0.5239355564117432, 0.465444952249527, 0.5870167016983032], [0.3010830879211426, 0.5227512717247009, 0.47175922989845276, 0.5860163569450378], [0.3555082678794861, 0.27816838026046753, 0.7346047163009644, 0.39062798023223877], [0.12581518292427063, 0.16863855719566345, 0.9488135576248169, 0.8527395725250244], [0.3640589714050293, 0.2795614004135132, 0.7338936924934387, 0.3891977071762085], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], 'num_detections': [14.0], 'detection_scores': [0.9795929193496704, 0.9508070349693298, 0.9276410341262817, 0.9104766249656677, 0.8870362043380737, 0.824179470539093, 0.7040495872497559, 0.6604017615318298, 0.5824876427650452, 0.48015695810317993, 0.4105406105518341, 0.39919009804725647, 0.362751305103302, 0.3524312376976013, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
    input_tensor = tf.convert_to_tensor(img)
    input_tensor = input_tensor[tf.newaxis, ...]
    output_dict = model(input_tensor)
    n_detections = int(output_dict['num_detections'])
    for key in output_dict.keys():
        if key != "num_detections":
            output_dict[key] = output_dict[key].numpy().squeeze().tolist()[:n_detections]
    output_dict["num_detections"] = n_detections
    # scale coordinates to proper image scale
    height, width, _ = img.shape
    hwhw = np.array([height, width, height, width]).reshape(1, 4)
    boxes = np.array(output_dict['detection_boxes'])
    scaled_coords = np.array(hwhw * boxes).astype("int")
    scaled_coords = scaled_coords.reshape(scaled_coords.shape[:-1] + (2, 2))
    scaled_coords = scaled_coords[:,:,[1,0]].tolist()
    output_dict["detection_boxes"] = scaled_coords
    return output_dict







