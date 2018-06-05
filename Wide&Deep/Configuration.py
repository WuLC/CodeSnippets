import os
import platform
class Configuration:
    """A class that stores variables specified by user"""
    def __init__(self):
        # which dataset to use
        self.dataset = 'criteo' # avazu, ipinyou

        # environment of visdom
        self.visualize = True
        self.env = self.dataset

        # data info
        self.num_train = 1200000# 150000 # 3000000
        self.num_val =   160000 # 20000   #400000
        if platform.system() == 'Linux':
            self.data_dir = '/mnt/e/dataset/{0}'.format(self.dataset)
            self.model_dir = '/mnt/e/{0}_saved_models'.format(self.num_train)
        elif platform.system() == 'Windows':
            self.data_dir = 'E:/dataset/{0}'.format(self.dataset)
            self.model_dir = 'E:/{0}_saved_models'.format(self.num_train)
        self.num_continous_feature = 13
        self.num_categorical_feature = 26
        self.train_file = os.path.join(self.data_dir, 'sub_train_{0}.txt'.format(self.num_train))
        self.val_file = os.path.join(self.data_dir, 'sub_val_{0}.txt'.format(self.num_val))
        self.test_file = ''
        
        # training parameters
        self.epochs = 200
        self.batch_size = 12
        self.epochs_between_evals = 2
        self.learning_rate = 0.01
        self.l1_regularization_strength = 0.1
        self.l2_regularization_strength = 0.1
        self.num_readers = 5

        # model parameters
        self.model_type = 'wide' # 'wide', 'deep' or 'wdl'
        self.use_fm_vector = False  # initialize embedding layer with latent vector obtained by FM
        self.hidden_units = [100, 75, 50, 25] # hidden units for deep part
        self.max_hash_size = 1000000
        self.embedding_size = 12
        self.loss_fn = 'log_loss' # weighted_log_loss, log_loss, focal_loss
        self.drop_out = 0.0 # drop_out_rate