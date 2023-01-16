import os

import dgl
import matplotlib.pyplot as plt
import torch
from torch.nn.functional import binary_cross_entropy_with_logits as BCELoss
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset.graph_dataset import GraphDataset
from nn.dgl.gae.gae import GAE


def collate(samples):
    bg = dgl.batch(samples)
    return bg


class Trainer:
    def __init__(self, model, lr):
        self.model = model
        self.optim = torch.optim.Adam(self.model.parameters(), lr=lr)
        print('Total Parameters:', sum([p.nelement() for p in self.model.parameters()]))

    def iteration(self, g, train=True):
        adj = g.adjacency_matrix().to_dense()
        # alleviate imbalance
        pos_weight = ((adj.shape[0] * adj.shape[0] - adj.sum()) / adj.sum())
        adj_logits = self.model.forward(g)
        loss = BCELoss(adj_logits, adj, pos_weight=pos_weight)
        if train:
            self.optim.zero_grad()
            loss.backward(retain_graph=True)
            self.optim.step()
        return loss.item()

    def save(self, epoch, save_dir):
        output_path = os.path.join(save_dir, 'ep{:02}.pkl'.format(epoch))
        torch.save(self.model.state_dict(), output_path)


def plot(train_losses):
    plt.plot(train_losses, label='train')
    plt.legend()
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.grid()
    plt.show()
    plt.savefig('train_loss.png')


def main(data_dir: str, batch_size: int, n_epochs: int, save_dir: str, lr: float = 1e-3):
    if not os.path.exists(save_dir):
        os.makedirs(os.path.join(save_dir, 'zinc250k.png'))

    print('Loading data')
    dataset = GraphDataset(data_dir)

    in_dim = dataset.global_graph_loader.nodes_features_tensor.shape[1]
    hidden_dims = [in_dim, 64]

    model = GAE(in_dim, hidden_dims)

    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate)
    trainer = Trainer(model, lr)
    train_losses, val_losses = [], []
    print('Training Start')
    for epoch in tqdm(range(n_epochs)):
        train_loss = 0
        model.train()
        for bg in tqdm(train_loader):
            bg.set_e_initializer(dgl.init.zero_initializer)
            bg.set_n_initializer(dgl.init.zero_initializer)
            train_loss += trainer.iteration(bg)
        train_loss /= len(train_loader)
        train_losses.append(train_loss)
        trainer.save(epoch, save_dir)

        val_loss = 0
        model.eval()

        print('Epoch: {:02d} | Train Loss: {:.4f}'.format(epoch, train_loss))
    plot(train_losses)


if __name__ == '__main__':
    data_dir = '/Users/marvzhang/projects/crawlab-team/auto-html/data/quotes.toscrape.com'
    main(
        data_dir=data_dir,
        batch_size=10,
        n_epochs=50,
        save_dir='/Users/marvzhang/projects/crawlab-team/auto-html/.models',
        lr=1e-4,
    )
