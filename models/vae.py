import torch


class Decoder(torch.nn.Module):
    def __init__(self, img_channels, latent_size, dimension):
        super().__init__()
        self.latent_size = latent_size
        self.img_channels = img_channels
        self.dimension = dimension

        self.fc1 = torch.nn.Linear(latent_size, 2048)

        if dimension == '1d':
            # self.deconv1 = torch.nn.ConvTranspose1d(1024, 128, 5, stride=2)
            self.deconv1 = torch.nn.ConvTranspose1d(2048, 1024, 2, stride=1)
            # self.deconv2 = torch.nn.ConvTranspose1d(128, 64, 5, stride=2)
            self.deconv2 = torch.nn.ConvTranspose1d(1024, 512, 2, stride=1)
            # self.deconv3 = torch.nn.ConvTranspose1d(64, 32, 6, stride=2)
            self.deconv3 = torch.nn.ConvTranspose1d(512, 256, 2, stride=1)
            self.deconv4 = torch.nn.ConvTranspose1d(256, 128, 1, stride=1)
            self.deconv5 = torch.nn.ConvTranspose1d(128, 64, 1, stride=1)
            self.deconv6 = torch.nn.ConvTranspose1d(64, 32, 1, stride=1)
            self.deconv7 = torch.nn.ConvTranspose1d(32, img_channels, 1, stride=1)

        elif dimension == '2d':
            self.deconv1 = torch.nn.ConvTranspose2d(1024, 128, 5, stride=2)
            self.deconv2 = torch.nn.ConvTranspose2d(128, 64, 5, stride=2)
            self.deconv3 = torch.nn.ConvTranspose2d(64, 32, 6, stride=2)
            self.deconv4 = torch.nn.ConvTranspose2d(32, img_channels, 6, stride=2)

    def forward(self, x):
        x = torch.nn.functional.relu(self.fc1(x))

        if self.dimension == '1d': x = x.unsqueeze(-1)
        elif self.dimension == '2d': x = x.unsqueeze(-1).unsqueeze(-1)

        x = torch.nn.functional.relu(self.deconv1(x))
        x = torch.nn.functional.relu(self.deconv2(x))
        x = torch.nn.functional.relu(self.deconv3(x))
        x = torch.nn.functional.relu(self.deconv4(x))
        x = torch.nn.functional.relu(self.deconv5(x))
        x = torch.nn.functional.relu(self.deconv6(x))
        # x = torch.nn.functional.relu(self.deconv3(x))
        # reconstruction = torch.nn.functional.sigmoid(self.deconv4(x))
        reconstruction = torch.nn.functional.sigmoid(self.deconv7(x))
        return reconstruction


class Encoder(torch.nn.Module):
    def __init__(self, img_channels, latent_size, dimension):
        super().__init__()
        self.latent_size = latent_size
        self.img_channels = img_channels

        if dimension == '1d':
            # self.conv1 = torch.nn.Conv1d(img_channels, 32, 4, stride=2)
            self.conv1 = torch.nn.Conv1d(img_channels, 32, 2, stride=1)
            # self.conv2 = torch.nn.Conv1d(32, 64, 4, stride=2)
            self.conv2 = torch.nn.Conv1d(32, 64, 2, stride=1)
            # self.conv3 = torch.nn.Conv1d(64, 128, 4, stride=2)
            self.conv3 = torch.nn.Conv1d(64, 128, 2, stride=1)
            # self.conv4 = torch.nn.Conv1d(128, 256, 4, stride=2)
            self.conv4 = torch.nn.Conv1d(128, 256, 1, stride=1)
            self.conv5 = torch.nn.Conv1d(256, 512, 1, stride=1)
            self.conv6 = torch.nn.Conv1d(512, 1024, 1, stride=1)
            self.conv7 = torch.nn.Conv1d(1024, 2048, 1, stride=1)

        elif dimension == '2d':
            self.conv1 = torch.nn.Conv2d(img_channels, 32, 4, stride=2)
            self.conv2 = torch.nn.Conv2d(32, 64, 4, stride=2)
            self.conv3 = torch.nn.Conv2d(64, 128, 4, stride=2)
            self.conv4 = torch.nn.Conv2d(128, 256, 4, stride=2)

        self.fc_mu = torch.nn.Linear(2048, latent_size)
        self.fc_logsigma = torch.nn.Linear(2048, latent_size)

    def forward(self, x):
        x = torch.nn.functional.relu(self.conv1(x))
        x = torch.nn.functional.relu(self.conv2(x))
        x = torch.nn.functional.relu(self.conv3(x))
        x = torch.nn.functional.relu(self.conv4(x))
        x = torch.nn.functional.relu(self.conv5(x))
        x = torch.nn.functional.relu(self.conv6(x))
        x = torch.nn.functional.relu(self.conv7(x))

        x = x.view(x.size(0), -1)

        mu = self.fc_mu(x)
        logsigma = self.fc_logsigma(x)

        return mu, logsigma


class MODEL(torch.nn.Module):
    def __init__(self, img_channels, latent_size, dimension):
        super().__init__()
        self.encoder = Encoder(img_channels, latent_size, dimension)
        self.decoder = Decoder(img_channels, latent_size, dimension)

    def forward(self, x):
        mu, logsigma = self.encoder(x)
        sigma = logsigma.exp()
        eps = torch.randn_like(sigma)
        z = eps.mul(sigma).add_(mu)

        recon_x = self.decoder(z)
        return recon_x, mu, logsigma
