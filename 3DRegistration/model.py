import torch
import torch.nn as nn

class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()

        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(16),
            nn.Mish(),
            nn.Conv2d(16, 32, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(32),
            nn.Mish(),
        )

        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(64),
            nn.Mish(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(128),
            nn.Mish(),
        )

        self.linear = nn.Sequential(
            nn.Linear(128 * (256 // 16) * (256 // 16), 1024),
            nn.BatchNorm1d(1024),
            nn.Mish(),
            nn.Linear(1024, 6),
            nn.Tanh(),
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = torch.flatten(x, 1)
        x = self.linear(x)
        return x