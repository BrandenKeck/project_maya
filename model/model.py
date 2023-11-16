# Imports
import torch
import numpy as np
import pandas as pd
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim.lr_scheduler import ExponentialLR

# Dataset Class
class SkaterDataset(Dataset):
    def __init__(self, data, device='cuda:0'):
        s = []
        f = []
        l = []
        for d in data:
            s.append(d["seq"])
            f.append(d["flat"])
            l.append(d["label"])
        self.seqs = torch.tensor(np.array(s)).float().to(device)
        self.flats = torch.tensor(np.array(f)).float().to(device)
        self.labels = torch.tensor(np.array(l)).float().to(device)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        seq = self.seqs[idx]
        flat = self.flats[idx]
        label = self.labels[idx]
        return seq, flat, label

class RNNModel(nn.Module):

    def __init__(self, 
                 seq_features = 13, 
                 flat_features = 10,
                 hidden_size = 41,
                 num_layers = 2,
                 dropout=0.2, device="cuda:0"):
        super(RNNModel, self).__init__()
        self.device = device
        self.seq_features = seq_features
        self.flat_features = flat_features
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.feedforward_size = flat_features+hidden_size
        self.drop = nn.Dropout(p=dropout)
        self.lrelu = nn.LeakyReLU()
        self.rnn = nn.RNN(seq_features, hidden_size, dropout=dropout, num_layers=2, batch_first=True)
        self.fc1 = nn.Linear(self.feedforward_size, int(self.feedforward_size/2))
        self.fc2 = nn.Linear(int(self.feedforward_size/2), int(self.feedforward_size/4))
        self.fc3 = nn.Linear(int(self.feedforward_size/4), 5)
     
    def forward(self, sequences, flat_data):
        h0 = torch.zeros(self.num_layers, sequences.size(0), self.hidden_size).to(self.device)
        x, _ = self.rnn(sequences, h0)
        x = torch.reshape(x[:, -1, :], (-1, self.hidden_size))
        x = torch.cat([x, flat_data], dim=1)
        x = self.lrelu(self.fc1(x))
        x = self.drop(x)
        x = self.lrelu(self.fc2(x))
        return F.softmax(self.fc3(x))
    
# Model Class
class SkaterModel():

    # Init Network Class
    def __init__(self, id,
                 dropout=0.2, 
                 learning_rate=4.12E-4, lr_decay=4.12E-5,
                 batch_size=10, epochs=2000, device="cuda:0"):
        
        # Model Components
        self.model = RNNModel(dropout=dropout, device=device).to(device)
        
        # Parameters
        self.id = id
        self.lr = learning_rate
        self.lr_decay = lr_decay
        self.batch_size = batch_size
        self.epochs = epochs
        self.device = device
    
    # Training Functions
    def train_network(self, data, verbose=True):
        
        # Training Algorithms
        self.model.train()
        ll = nn.CrossEntropyLoss()
        oo = optim.AdamW(self.model.parameters(), lr=self.lr)
        ss = ExponentialLR(oo, gamma=self.lr_decay)
        dataloader = DataLoader(data, batch_size=self.batch_size, shuffle=True)

        # Epoch Loop
        for epoch in range(self.epochs):
            
            # Training Loop
            totalloss = 0.0
            for i, (sequences, flat_data, labels) in enumerate(dataloader):
                labels = torch.reshape(labels, (-1, 5)).float()
                oo.zero_grad()
                outputs = self.model(sequences, flat_data)
                loss = ll(outputs, labels)
                loss.backward()
                oo.step()
                totalloss += loss.item()
            totalloss = totalloss / i

            # Learning Rate Schedule (Deafault 0)
            ss.step()

            # Print Epochs If Verbose            
            if verbose: print(f'[{epoch + 1}/{self.epochs}] Loss: {totalloss / i}')

    # Run metrics on the test set only
    def predict_network(self, data):
        self.model.eval()
        # TODO

    # Save network to disc
    def save(self):
        torch.save(self.model.state_dict(), f"./model/models/{self.id}")
    
    # Load network from disc
    def load(self):
        self.model.load_state_dict(torch.load(f"./model/models/{self.id}", map_location=torch.device(self.device)))
