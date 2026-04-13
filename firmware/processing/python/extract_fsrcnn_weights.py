import cv2
import numpy as np
import os

def extract_fsrcnn_weights(model_path, output_file):
    net = cv2.dnn.readNet(model_path)
    
    # Based on previous logs, biases are in 'add', 'add_2', etc.
    # We will try to match conv layers with their corresponding add and mul layers
    mapping = [
        ('conv1', 'add', 'mul'),
        ('conv2', 'add_2', 'mul_2'),
        ('conv3', 'add_4', 'mul_4'),
        ('conv4', 'add_6', 'mul_6'),
        ('conv5', 'add_8', 'mul_8'),
        ('conv6', 'add_10', 'mul_10'),
        ('conv7', 'add_12', 'mul_12'),
        ('conv8', None, None) # Deconv might handle bias differently or not have one
    ]
    
    with open(output_file, 'wb') as f:
        for conv_name, add_name, mul_name in mapping:
            try:
                # Weights
                conv_layer = net.getLayer(net.getLayerId(conv_name))
                weights = conv_layer.blobs[0]
                weights.tofile(f)
                print(f"Extracted weights for {conv_name}, shape: {weights.shape}")
                
                # Bias
                if add_name:
                    add_layer = net.getLayer(net.getLayerId(add_name))
                    bias = add_layer.blobs[0]
                    bias.tofile(f)
                    print(f"  Extracted bias from {add_name}, shape: {bias.shape}")
                else:
                    # Dummy bias for Deconv if not found
                    np.zeros(weights.shape[0], dtype=np.float32).tofile(f)
                    print(f"  Using dummy bias for {conv_name}")
                
                # PReLU slope
                if mul_name:
                    mul_layer = net.getLayer(net.getLayerId(mul_name))
                    slope = mul_layer.blobs[0]
                    slope.tofile(f)
                    print(f"  Extracted slope from {mul_name}, shape: {slope.shape}")
                
            except Exception as e:
                print(f"Error extracting group {conv_name}: {e}")

if __name__ == "__main__":
    extract_fsrcnn_weights("firmware/processing/models/FSRCNN_x2.pb", "firmware/processing/C/models/fsrcnn_weights.bin")
