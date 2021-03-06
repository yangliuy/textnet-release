#-*-coding:utf8-*-
import copy, os

from gen_conf_file import *
from dataset_cfg import *

def gen_match_lstm(d_mem, init, lr, dataset, l2, lstm_norm2, is_pretrain, pretrain_run_no, model_no, epoch_no):
    # print "ORC: left & right lstm share parameters"
    net = {}

    ds = DatasetCfg(dataset)
    g_filler    = gen_uniform_filter_setting(init)
    zero_filler = gen_zero_filter_setting()
    g_updater   = gen_adagrad_setting(lr = lr, l2 = l2, batch_size = ds.train_batch_size)
    zero_l2_updater   = gen_adagrad_setting(lr = lr, batch_size = ds.train_batch_size)

    g_layer_setting = {}
    g_layer_setting['no_bias'] = False
    g_layer_setting['w_filler'] = g_filler 
    g_layer_setting['u_filler'] = g_filler
    g_layer_setting['b_filler'] = zero_filler
    g_layer_setting['w_updater'] = g_updater
    g_layer_setting['u_updater'] = g_updater
    g_layer_setting['b_updater'] = g_updater
    g_layer_setting['w_g_filler'] = g_filler 
    g_layer_setting['u_g_filler'] = g_filler
    g_layer_setting['b_g_filler'] = zero_filler
    g_layer_setting['w_c_filler'] = g_filler 
    g_layer_setting['u_c_filler'] = g_filler
    g_layer_setting['b_c_filler'] = zero_filler
    g_layer_setting['w_g_updater'] = g_updater
    g_layer_setting['u_g_updater'] = g_updater
    g_layer_setting['b_g_updater'] = g_updater
    g_layer_setting['w_c_updater'] = g_updater
    g_layer_setting['u_c_updater'] = g_updater
    g_layer_setting['b_c_updater'] = g_updater


    net['net_name'] = 'match_bilstm_sim_dpool'
    net['need_reshape'] = True 
    net_cfg_train, net_cfg_valid, net_cfg_test = {}, {}, {}
    net['net_config'] = [net_cfg_train, net_cfg_valid, net_cfg_test]
    net_cfg_train["tag"] = "Train"
    net_cfg_train["max_iters"] = ds.train_max_iters 
    net_cfg_train["display_interval"] = ds.train_display_interval
    net_cfg_train["out_nodes"] = ['loss']
    net_cfg_valid["tag"] = "Valid"
    net_cfg_valid["max_iters"] = ds.valid_max_iters 
    net_cfg_valid["display_interval"] = ds.valid_display_interval 
    net_cfg_valid["out_nodes"] = ['P@k','MRR']
    net_cfg_test["tag"] = "Test"
    net_cfg_test["max_iters"]  = ds.test_max_iters 
    net_cfg_test["display_interval"] = ds.test_display_interval
    net_cfg_test["out_nodes"]  = ['P@k', 'MRR']
    layers = []
    net['layers'] = layers

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = []
    layer['top_nodes'] = ['x', 'y']
    layer['layer_name'] = 'train_data'
    layer['layer_type'] = 79
    layer['tag'] = ['Train']
    setting = {}
    layer['setting'] = setting
    setting['batch_size'] = ds.train_batch_size
    setting['shuffle'] = True
    setting['data_file'] = ds.train_data_file
    setting['max_doc_len'] = ds.max_doc_len
    setting['min_doc_len'] = ds.min_doc_len

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = []
    layer['top_nodes'] = ['x', 'y']
    layer['layer_name'] = 'valid_data'
    layer['layer_type'] = 80 
    layer['tag'] = ['Valid']
    setting = {}
    layer['setting'] = setting
    setting['data_file'] = ds.valid_data_file
    setting['max_doc_len'] = ds.max_doc_len
    setting['min_doc_len'] = ds.min_doc_len

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = []
    layer['top_nodes'] = ['x', 'y']
    layer['layer_name'] = 'test_data'
    layer['layer_type'] = 80 
    layer['tag'] = ['Test']
    setting = {}
    layer['setting'] = setting
    setting['data_file'] = ds.test_data_file
    setting['max_doc_len'] = ds.max_doc_len
    setting['min_doc_len'] = ds.min_doc_len

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['x']
    layer['top_nodes'] = ['word_rep_seq']
    layer['layer_name'] = 'embedding'
    layer['layer_type'] = 21
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['embedding_file'] = ds.embedding_file
    print "ORC: update all words"
    # setting['update_indication_file'] = ds.update_indication_file
    setting['feat_size'] = ds.d_word_rep
    setting['word_count'] = ds.vocab_size
    print "ORC: not use l2 for embedding"
    setting['w_updater'] = zero_l2_updater

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['word_rep_seq']
    layer['top_nodes'] = ['l_lstm_seq']
    layer['layer_name'] = 'l_lstm'
    # layer['layer_type'] = 24
    layer['layer_type'] = 1006 # gru
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['d_mem'] = d_mem
    setting['grad_norm2'] = lstm_norm2
    setting['grad_cut_off'] = 100
    setting['max_norm2'] = 100
    setting['reverse'] = False
    setting['f_gate_bias_init'] = 0.
    setting['o_gate_bias_init'] = 0.

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['l_lstm_seq']
    layer['top_nodes'] = ['l_pool_rep']
    layer['layer_name'] = 'l_wholePooling'
    layer['layer_type'] =  25
    setting = {"pool_type":"last"}
    layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['word_rep_seq']
    layer['top_nodes'] = ['r_lstm_seq']
    layer['layer_name'] = 'r_lstm'
    # layer['layer_type'] = 24
    layer['layer_type'] = 1006 # gru
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['d_mem'] = d_mem
    setting['grad_norm2'] = lstm_norm2
    setting['reverse'] = True 
    setting['grad_cut_off'] = 100
    setting['max_norm2'] = 100
    setting['f_gate_bias_init'] = 0.
    setting['o_gate_bias_init'] = 0.

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['r_lstm_seq']
    layer['top_nodes'] = ['r_pool_rep']
    layer['layer_name'] = 'r_wholePooling'
    layer['layer_type'] =  25
    setting = {"pool_type":"first"}
    layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['l_pool_rep', 'r_pool_rep']
    layer['top_nodes'] = ['bi_pool_rep']
    layer['layer_name'] = 'concat'
    layer['layer_type'] = 18
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['bottom_node_num'] = 2
    setting['concat_dim_index'] = 3

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['bi_pool_rep']
    layer['top_nodes'] = ['hidden_trans']
    layer['layer_name'] = 'mlp_hidden'
    layer['layer_type'] = 11 
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['num_hidden'] = d_mem * 2
    # setting['no_bias'] = False

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['hidden_trans']
    layer['top_nodes'] = ['hidden_rep']
    layer['layer_name'] = 'hidden_nonlinear'
    layer['layer_type'] = 3 
    setting = {}
    layer['setting'] = setting
     
    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['hidden_rep']
    layer['top_nodes'] = ['softmax_prob']
    layer['layer_name'] = 'softmax_fullconnect'
    layer['layer_type'] = 11 
    setting = copy.deepcopy(g_layer_setting)
    layer['setting'] = setting
    setting['num_hidden'] = 1 # ds.num_class
    # setting['no_bias'] = False
    setting['w_filler'] = zero_filler

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['softmax_prob', 'y']
    layer['top_nodes'] = ['loss']
    # layer['layer_name'] = 'softmax_activation'
    layer['layer_name'] = 'pair_hinge'
    layer['layer_type'] = 55
    layer['tag'] = ['Train'] 
    setting = {}
    layer['setting'] = setting
    setting['delta'] = 1.

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['softmax_prob', 'y']
    layer['top_nodes'] = ['P@k']
    layer['layer_name'] = 'P@k_layer'
    layer['layer_type'] = 61 
    layer['tag'] = ['Valid', 'Test'] 
    setting = {'k':1, 'col':0, 'method':'P@k'}
    layer['setting'] = setting

    layer = {}
    layers.append(layer) 
    layer['bottom_nodes'] = ['softmax_prob', 'y']
    layer['top_nodes'] = ['MRR']
    layer['layer_name'] = 'MRR_layer'
    layer['layer_type'] = 61 
    layer['tag'] = ['Valid', 'Test'] 
    setting = {'k':1, 'col':0, 'method':'MRR'}
    layer['setting'] = setting

    return net

run = 1
l2 = 0.
# for dataset in ['paper']:
for dataset in ['qa_50']:
# for dataset in ['qa_candi']:
    for d_mem in [50]:
        idx = 0
        # for model_no in [0,1,2,3,4,5,6,7,8]:
        #     for epoch_no in [20000, 40000, 80000]:
        for model_no in [2]:
            #  for epoch_no in [0, 10000, 25000]:
            for epoch_no in [0]:
                # for init in [0.5, 0.3, 0.1]:
                for init in [0.3, 0.1, 0.03]:
                    for lr in [0.5, 0.3, 0.1]:
                        # for l2 in [0.00001, 0.0001]:
                        for l2 in [0]:
                            pretrain_run_no = 18
                            lstm_norm2 = 10000 
                            net = gen_match_lstm(d_mem=d_mem,init=init,lr=lr,dataset=dataset,l2=l2,lstm_norm2=lstm_norm2,  \
                                                 is_pretrain=False,pretrain_run_no=pretrain_run_no,model_no=model_no,epoch_no=epoch_no)
                            net['log'] = 'log.match.bilstm_mlp.{0}.d{1}.run{2}.{3}'.format\
                                         (dataset, str(d_mem), str(run), str(idx))
                            gen_conf_file(net, '/home/wsx/exp/match/{0}/bilstm_mlp/run.{1}/'.format(dataset,str(run)) + \
                                               'model.match.bilstm_mlp.{0}.d{1}.run{2}.{3}'.format\
                                               (dataset, str(d_mem), str(run), str(idx)))
                            idx += 1
