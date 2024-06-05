import os
from ultralytics import YOLO
from django.conf import settings


class ComputerVision:
    def __init__(self, output_dir, conf=0.2):
        self.model_dir = os.path.join("chat", "CV_Model", "yolov8n.pt")
        self.output_dir = output_dir
        self.task = "detect"
        self.conf = conf
        self.imgsz = 256
        self.class_list = [
            "Acne",
            "Brown-patches",
            "Inflamed-patches-with-silver-scales",
            "Molluscum-contagiosum",
            "Nail",
            "Postule",
            "Ringworm",
            "Rosacea",
            "Scalp",
            "Scaly",
            "Sweat",
            "Vitiligo",
            "Warts",
            "Welts",
        ]
        self.all_classes = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            4: "airplane",
            5: "bus",
            6: "train",
            7: "truck",
            8: "boat",
            9: "traffic light",
            10: "fire hydrant",
            11: "stop sign",
            12: "parking meter",
            13: "bench",
            14: "bird",
            15: "cat",
            16: "dog",
            17: "horse",
            18: "sheep",
            19: "cow",
            20: "elephant",
            21: "bear",
            22: "zebra",
            23: "giraffe",
            24: "backpack",
            25: "umbrella",
            26: "handbag",
            27: "tie",
            28: "suitcase",
            29: "frisbee",
            30: "skis",
            31: "snowboard",
            32: "sports ball",
            33: "kite",
            34: "baseball bat",
            35: "baseball glove",
            36: "skateboard",
            37: "surfboard",
            38: "tennis racket",
            39: "bottle",
            40: "wine glass",
            41: "cup",
            42: "fork",
            43: "knife",
            44: "spoon",
            45: "bowl",
            46: "banana",
            47: "apple",
            48: "sandwich",
            49: "orange",
            50: "broccoli",
            51: "carrot",
            52: "hot dog",
            53: "pizza",
            54: "donut",
            55: "cake",
            56: "chair",
            57: "couch",
            58: "potted plant",
            59: "bed",
            60: "dining table",
            61: "toilet",
            62: "tv",
            63: "laptop",
            64: "mouse",
            65: "remote",
            66: "keyboard",
            67: "cell phone",
            68: "microwave",
            69: "oven",
            70: "toaster",
            71: "sink",
            72: "refrigerator",
            73: "book",
            74: "clock",
            75: "vase",
            76: "scissors",
            77: "teddy bear",
            78: "hair drier",
            79: "toothbrush",
        }

    def detect_diseases(self, classes):
        classes = classes[0]
        int_list = [int(x) for x in classes]
        detected_disease_list = [self.class_list[i] for i in int_list]
        return detected_disease_list

    def run_inference(self, input_paths_list):

        img_names = [os.path.split(path)[-1] for path in input_paths_list]
        print("img_names")
        print(img_names)
        print("=" * 100)
        print("input_paths_list")
        print(input_paths_list)
        print("len: ", len(input_paths_list))
        print("=" * 100)
        # classes = []
        model = YOLO(self.model_dir, task=self.task)
        results = model(source=input_paths_list, conf=self.conf, imgsz=self.imgsz)

        detected_symptoms = []

        for i in range(len(results)):
            im_name = f"output_{img_names[i]}"
            print(f"running inference for {im_name}")
            boxes = results[i].boxes
            class_ = boxes.cls
            # classes.append(class_.tolist())
            masks = results[i].masks
            keypoints = results[i].keypoints
            probs = results[i].probs
            
            symptoms_dict = {}
            symptoms_dict["img_name"] = im_name
            symptoms_dict["np_index"] = list(set(class_.tolist()))
            symptoms_dict["cls_name"] = [self.all_classes[ind] for ind in symptoms_dict["np_index"]]
            detected_symptoms.append(symptoms_dict)
            
            save_dir = os.path.join(self.output_dir, im_name)
            print(f"Saving {im_name}")
            results[i].save(filename=save_dir) ## Doubt - Do we need unique names?
            print(f"Saving complete for {im_name}")
            # detected_diseases[im_name] = list(set(self.detect_diseases(classes)))
        return detected_symptoms


# model_dir = os.path.join(settings.BASE_DIR, "chat", "CV_Model", "best.onnx")
# output_dir = os.path.join(settings.BASE_DIR,"chat" ,"Images", "Output")
# cv = CV(model_dir=model_dir, output_dir=output_dir)
# input_dir = os.path.join(settings.BASE_DIR, "chat", "Images", "Input", "sample_input.jpg")
# classes = cv.cv_model(input_dir)
