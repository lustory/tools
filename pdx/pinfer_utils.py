import paddle.inference as paddle_infer
import os
import numpy as np
import imutils
import cv2
from paddle.inference import Config
from paddle.inference import create_predictor


def pinfer_preprocess(image, img_size):
    
    def resize(img, target_size):
        """resize to target size"""
        if not isinstance(img, np.ndarray):
            raise TypeError('image type is not numpy.')
        im_shape = img.shape
        im_size_min = np.min(im_shape[0:2])
        im_size_max = np.max(im_shape[0:2])
        im_scale_x = float(target_size) / float(im_shape[1])
        im_scale_y = float(target_size) / float(im_shape[0])
        img = cv2.resize(img, None, None, fx=im_scale_x, fy=im_scale_y)
        return img


    def normalize(img, mean, std):
        img = img / 255.0
        mean = np.array(mean)[np.newaxis, np.newaxis, :]
        std = np.array(std)[np.newaxis, np.newaxis, :]
        img -= mean
        img /= std
        return img

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    
    img = resize(image, img_size)
    img = img[:, :, ::-1].astype('float32')  # bgr -> rgb
    img = normalize(img, mean, std)
    img = img.transpose((2, 0, 1))  # hwc -> chw
    
    scale_factor = np.array([img_size*1. / image.shape[0], \
                         img_size*1. / image.shape[1]]).reshape((1, 2)).astype(np.float32)
    
    img_shape = np.array([img_size, img_size]).reshape((1, 2)).astype(np.float32)
    
    return [img_shape, img[np.newaxis, :], scale_factor]


def pinfer_init_predictor(model_dir, model_file="model.pdmodel", params_files="model.pdiparams", gpu_mem=100, gpu_id=0, use_gpu=True):
#     model_dir = "/home/xjtu/.research/models/zybds_general_20210830/"
    model_file = os.path.join(model_dir, model_file)
    params_file = os.path.join(model_dir, params_files)

    config = Config(model_file, params_file)
    config.enable_memory_optim()
    if use_gpu:
        config.enable_use_gpu(gpu_mem, gpu_id)
    else:
        # If not specific mkldnn, you can set the blas thread.
        # The thread num should not be greater than the number of cores in the CPU.
        config.set_cpu_math_library_num_threads(4)
        config.enable_mkldnn()

    predictor = create_predictor(config)
    return predictor


def pinfer_run(predictor, img):
    # copy img data to input tensor
    input_names = predictor.get_input_names()
    for i, name in enumerate(input_names):
        input_tensor = predictor.get_input_handle(name)
        input_tensor.reshape(img[i].shape)
        input_tensor.copy_from_cpu(img[i].copy())

    # do the inference
    predictor.run()

    results = []
    # get out data from output tensor
    output_names = predictor.get_output_names()
    for i, name in enumerate(output_names):
        output_tensor = predictor.get_output_handle(name)
        output_data = output_tensor.copy_to_cpu()
        results.append(output_data)
    return results