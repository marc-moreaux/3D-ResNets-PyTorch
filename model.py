import torch
from torch import nn

from models import resnet, pre_act_resnet, wide_resnet, resnext, densenet


def generate_model(opt):
    assert opt.model in [
        'resnet', 'preresnet', 'wideresnet', 'resnext', 'densenet'
    ]

    if opt.model == 'resnet':
        assert opt.model_depth in [10, 18, 34, 50, 101, 152, 200]

        from models.resnet import get_fine_tuning_parameters

        args = {
            "num_classes": opt.n_classes,
            "shortcut_type": opt.resnet_shortcut,
            "sample_size": opt.sample_size,
            "sample_duration": opt.sample_duration}

        if opt.model_depth == 10:
            model = resnet.resnet10(**args)
        elif opt.model_depth == 18:
            model = resnet.resnet18(**args)
        elif opt.model_depth == 34:
            model = resnet.resnet34(**args)
        elif opt.model_depth == 50:
            model = resnet.resnet50(**args)
        elif opt.model_depth == 101:
            model = resnet.resnet101(**args)
        elif opt.model_depth == 152:
            model = resnet.resnet152(**args)
        elif opt.model_depth == 200:
            model = resnet.resnet200(**args)

    elif opt.model == 'wideresnet':
        assert opt.model_depth in [50]

        from models.wide_resnet import get_fine_tuning_parameters

        if opt.model_depth == 50:
            model = wide_resnet.resnet50(
                num_classes=opt.n_classes,
                shortcut_type=opt.resnet_shortcut,
                k=opt.wide_resnet_k,
                sample_size=opt.sample_size,
                sample_duration=opt.sample_duration)

    elif opt.model == 'resnext':
        assert opt.model_depth in [50, 101, 152]

        from models.resnext import get_fine_tuning_parameters

        args = {
            "num_classes": opt.n_classes,
            "shortcut_type": opt.resnet_shortcut,
            "cardinality": opt.resnext_cardinality,
            "sample_size": opt.sample_size,
            "sample_duration": opt.sample_duration}

        if opt.model_depth == 50:
            model = resnext.resnet50(**args)
        elif opt.model_depth == 101:
            model = resnext.resnet101(**args)
        elif opt.model_depth == 152:
            model = resnext.resnet152(**args)

    elif opt.model == 'preresnet':
        assert opt.model_depth in [18, 34, 50, 101, 152, 200]

        from models.pre_act_resnet import get_fine_tuning_parameters

        args = {
            "num_classes": opt.n_classes,
            "shortcut_type": opt.resnet_shortcut,
            "sample_size": opt.sample_size,
            "sample_duration": opt.sample_duration}

        if opt.model_depth == 18:
            model = pre_act_resnet.resnet18(**args)
        elif opt.model_depth == 34:
            model = pre_act_resnet.resnet34(**args)
        elif opt.model_depth == 50:
            model = pre_act_resnet.resnet50(**args)
        elif opt.model_depth == 101:
            model = pre_act_resnet.resnet101(**args)
        elif opt.model_depth == 152:
            model = pre_act_resnet.resnet152(**args)
        elif opt.model_depth == 200:
            model = pre_act_resnet.resnet200(**args)

    elif opt.model == 'densenet':
        assert opt.model_depth in [121, 169, 201, 264]

        from models.densenet import get_fine_tuning_parameters

        args = {
            "num_classes": opt.n_classes,
            "sample_size": opt.sample_size,
            "sample_duration": opt.sample_duration}

        if opt.model_depth == 121:
            model = densenet.densenet121(**args)
        elif opt.model_depth == 169:
            model = densenet.densenet169(**args)
        elif opt.model_depth == 201:
            model = densenet.densenet201(**args)
        elif opt.model_depth == 264:
            model = densenet.densenet264(**args)

    if opt.no_cuda:
        device = 'cpu'
    else:
        device = 'cuda'
        model = model.to(device)
        model = nn.DataParallel(model, device_ids=None)

    if opt.pretrain_path:
        print('loading pretrained model {}'.format(opt.pretrain_path))
        pretrain = torch.load(opt.pretrain_path, map_location=device)
        assert opt.arch == pretrain['arch']

        model.load_state_dict(pretrain['state_dict'])

        if opt.model == 'densenet':
            model.module.classifier = nn.Linear(
                model.module.classifier.in_features, opt.n_finetune_classes)
            model.module.classifier = model.module.classifier.to(device)
        else:
            model.module.fc = nn.Linear(model.module.fc.in_features,
                                        opt.n_finetune_classes)
            model.module.fc = model.module.fc.to(device)

        parameters = get_fine_tuning_parameters(model, opt.ft_begin_index)
        return model, parameters

    return model, model.parameters()
