import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from tqdm import tqdm
from model import ConvNet



class CustomDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.data_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.data_frame.iloc[idx, -1])
        image = Image.open(img_name)
        labels = torch.tensor(self.data_frame.iloc[idx, :6], dtype=torch.float32)
        
        if self.transform:
            image = self.transform(image)

        return image, labels

# 定义数据集的路径和转换
csv_file = 'Dataset/MedModels/0014_H_AO_COA/tau_data.csv'
image_dir = 'Dataset/MedModels/0014_H_AO_COA/imgdata'

# 使用transforms来对图像进行预处理
transform = transforms.Compose([
    transforms.Resize((256, 256)),  # 调整图像大小
    transforms.ToTensor(),  # 将图像转换为PyTorch张量
])

# 创建自定义数据集
custom_dataset = CustomDataset(csv_file=csv_file, root_dir=image_dir, transform=transform)

# 使用DataLoader来加载数据
batch_size = 4
data_loader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=True)


def train(model, data_loader, loss_fn, optimizer, num_epochs):
    print("Start training...")
    for epoch in range(num_epochs):
        loss_sum = 0.0
        for imgs, labels in data_loader:

            imgs = imgs.to(device)
            labels = labels.to(device)

            outputs = model(imgs)
            loss = loss_fn(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            loss_sum += loss.item() * imgs.size(0)

        epoch_loss = loss_sum / len(data_loader.dataset)
        print(f"Epoch #{epoch + 1} Loss: {epoch_loss:.4f}")


model_path = '3DRegistration/models/convnet.pth'
# 定义模型
model = ConvNet()

# # 读取模型
# model.load_state_dict(torch.load(model_path))

# 定义损失函数
loss_fn = torch.nn.MSELoss()

# 定义优化器
learning_rate = 1e-3
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# 转移到GPU
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Using device {device}")
model.to(device)

# 训练模型
train(model, data_loader, loss_fn, optimizer, num_epochs=10)

# 保存模型
torch.save(model.state_dict(), model_path)
