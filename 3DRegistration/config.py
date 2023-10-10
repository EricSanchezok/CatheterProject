import torch    

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

W = 1280
H = 720

FX = 899.62
FY = 899.905

CX = 650.548
CY = 357.754

PATH_IMG = "Dataset/MedModels/0014_H_AO_COA/imgdata/"
IMG_NAME = "image_38.jpg"
PATH_MESH = 'Dataset/MedModels/0014_H_AO_COA/Models/0102_0001.stl'

SACLE_FACTOR = 20.0
NEAR, FAR = 10, 2000.0
M = 100

MAX_ITERATIONS = 1000

K1 = 0.143195
K2 = -0.472782
P1 = 0.00055683
P2 = -0.000497228
K3 = 0.423885