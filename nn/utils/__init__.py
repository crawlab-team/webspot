import torch
import torch.nn.functional as F


def step(model, optimizer, features, adj, idx_train, labels):
    model.train()
    optimizer.zero_grad()
    output = model(features, adj)
    loss = F.cross_entropy(output[idx_train], labels[idx_train])
    acc = accuracy(output[idx_train], labels[idx_train])
    loss.backward()
    optimizer.step()
    return loss.item(), acc
