import dgl.function as fn
import torch
import torch.nn as nn
import torch.nn.functional as F


class NodeApplyModule(nn.Module):
    def __init__(self, in_feats, out_feats, activation):
        super(NodeApplyModule, self).__init__()
        self.linear = nn.Linear(in_feats, out_feats)
        self.activation = activation

    def forward(self, node):
        h = self.linear(node.data['h'])
        h = self.activation(h)
        return {'h': h}


gcn_msg = fn.copy_src(src='h', out='m')
gcn_reduce = fn.sum(msg='m', out='h')  # sum aggregation


class GCN(nn.Module):
    def __init__(self, in_feats, out_feats, activation):
        super(GCN, self).__init__()
        self.apply_mod = NodeApplyModule(in_feats, out_feats, activation)

    def forward(self, g, feature):
        g.ndata['h'] = feature
        g.update_all(gcn_msg, gcn_reduce)
        g.apply_nodes(func=self.apply_mod)
        h = g.ndata.pop('h')
        return h


class GAE(nn.Module):
    def __init__(self, in_dim, hidden_dims):
        super(GAE, self).__init__()
        if len(hidden_dims) >= 2:
            layers = [GCN(in_dim, hidden_dims[0], F.relu)]
            for i in range(1, len(hidden_dims)):
                if i != len(hidden_dims) - 1:
                    layers.append(GCN(hidden_dims[i - 1], hidden_dims[i], F.relu))
                else:
                    layers.append(GCN(hidden_dims[i - 1], hidden_dims[i], lambda x: x))
        else:
            layers = [GCN(in_dim, hidden_dims[0], lambda x: x)]
        self.layers = nn.ModuleList(layers)
        self.decoder = InnerProductDecoder(activation=lambda x: x)

    def forward(self, g):
        if g.ndata.get('h') is None:
            g.ndata['h'] = g.ndata['feat'].to(torch.float32)
        h = g.ndata['h']
        for conv in self.layers:
            g.ndata['h'] = conv(g, h)
        g.ndata['h'] = h
        adj_rec = self.decoder(h)
        return adj_rec

    def encode(self, g):
        h = g.ndata['h']
        for conv in self.layers:
            h = conv(g, h)
        return h


class InnerProductDecoder(nn.Module):
    def __init__(self, activation=torch.sigmoid, dropout=0.1):
        super(InnerProductDecoder, self).__init__()
        self.dropout = dropout
        self.activation = activation

    def forward(self, z):
        z = F.dropout(z, self.dropout)
        adj = self.activation(torch.mm(z, z.t()))
        return adj
