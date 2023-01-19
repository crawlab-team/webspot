from torch import nn
from dgl.nn.pytorch import GATConv
from torch.nn.functional import mish


class DglGATModel(nn.Module):
    def __init__(
            self,
            number_layers,
            in_dim,
            num_hidden,
            num_classes,
            heads,
            activation,
            feat_drop,
            attn_drop,
            negative_slope,
            residual,
    ):
        super(DglGATModel, self).__init__()

        # settings
        self.number_layers = number_layers
        self.in_dim = in_dim
        self.num_hidden = num_hidden
        self.num_classes = num_classes
        self.heads = heads
        self.activation = activation
        self.feat_drop = feat_drop
        self.attn_drop = attn_drop
        self.negative_slope = negative_slope
        self.residual = residual

        # GAT layers
        self.gat_layers = nn.ModuleList()

        # input layer
        self.gat_layers.append(GATConv(
            in_dim,
            num_hidden,
            heads[0],
            feat_drop,
            attn_drop,
            negative_slope,
            residual,
            activation,
        ))

        # hidden layers
        for i in range(1, number_layers):
            self.gat_layers.append(GATConv(
                num_hidden * heads[i - 1],
                num_hidden,
                heads[i],
                feat_drop,
                attn_drop,
                negative_slope,
                residual,
                activation,
            ))

        # output layer
        self.gat_layers.append(GATConv(
            num_hidden * heads[-2],
            num_classes,
            heads[-1],
            feat_drop,
            attn_drop,
            negative_slope,
            residual,
            None,
        ))

    def forward(self, g, inputs):
        h = inputs
        for i in range(self.number_layers):
            h = self.gat_layers[i](g, h).flatten(1)
        logits = self.gat_layers[-1](g, h).mean(1)
        return logits


def get_gat_model():
    num_heads = 8
    num_layers = 1
    num_out_heads = 1
    heads = ([num_heads] * num_layers) + [num_out_heads]
    return DglGATModel(
        number_layers=num_layers + 1,
        in_dim=1,
        num_hidden=8,
        num_classes=1,
        heads=heads,
        activation=mish,
        feat_drop=0.6,
        attn_drop=0.6,
        negative_slope=0.2,
        residual=False,
    )


if __name__ == '__main__':
    model = get_gat_model()
    print(model)
