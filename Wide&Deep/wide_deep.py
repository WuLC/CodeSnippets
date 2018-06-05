# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Example code for TensorFlow Wide & Deep Tutorial using tf.estimator API."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil
import platform
from time import gmtime, strftime

import fire
import visdom
import tensorflow as tf
import numpy as np
from sklearn import  metrics

from dnn_linear_combined import DNNLinearCombinedClassifier
from Configuration import Configuration

# use GPU under windows
if platform.system() == 'Windows': 
    os.environ["CUDA_VISIBLE_DEVICES"]='0'

CONF = Configuration()

if CONF.dataset == 'criteo':
    _CSV_COLUMNS = [
    'label',
    'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12',
    'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'd11', 'd12', 'd13',
    'd14', 'd15', 'd16', 'd17', 'd18', 'd19', 'd20', 'd21', 'd22', 'd23', 'd24', 'd25'
    ]
elif CONF.dataset == 'avazu':
    _CSV_COLUMNS = [
                    'id', 'click', 'hour', 'C1', 'banner_pos', 'site_id', 'site_domain', 'site_category', 'app_id', 'app_domain',
                    'app_category', 'device_id', 'device_ip', 'device_model', 'device_type', 'device_conn_type',
                    'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21'
                   ]

_CSV_COLUMN_DEFAULTS = [[0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0],
                        ['missed'], ['missed'], ['missed'], ['missed'], ['missed'], ['missed'], 
                        ['missed'], ['missed'], ['missed'], ['missed'], ['missed'], ['missed'],
                        ['missed'], ['missed'], ['missed'], ['missed'], ['missed'], ['missed'],
                        ['missed'], ['missed'], ['missed'], ['missed'], ['missed'], ['missed'],
                        ['missed'], ['missed']]


def hash_size_of_cate_feature():
    cate_set = [set() for _ in range(26)]
    with open(CONF.train_file, mode='r', encoding='utf8') as rf:
        for line in rf:
            blocks = line.rstrip('\n').split(',') # line.strip().split('\t) will cause error
            for i in range(14, 40):
                cate_set[i-14].add(blocks[i])
    with open(CONF.val_file, mode='r', encoding='utf8') as rf:
        for line in rf:
            blocks = line.rstrip('\n').split(',') # line.strip().split('\t) will cause error
            for i in range(14, 40):
                cate_set[i-14].add(blocks[i])
    unique_count = [len(s) for s in cate_set]
    hash_size = []
    for i in range(len(unique_count)):
        hs = 10
        while hs < unique_count[i] and hs < CONF.max_hash_size:
            hs <<= 1
        hash_size.append(hs)
    return hash_size


def load_fm_embedding():
    fm_vector_file = '/mnt/e/FM&FFM/fm_vector_{0}_{1}'.format(CONF.embedding_size, CONF.num_train)
    embedding = []
    count = 0
    with open(fm_vector_file, encoding='utf8', mode = 'r') as rf:
        for line in rf:
            blocks = line.strip().split()
            if len(blocks) == CONF.embedding_size:
                count += 1
                if count <= CONF.num_continous_feature: # skip embedding for continous feature 
                    continue
                embedding.append([float(num) for num in blocks])
    total_hash_size = sum(hash_size_of_cate_feature())
    assert total_hash_size >= len(embedding), 'Not legal, total hash size smaller than hashed slots'
    for _ in range(total_hash_size - len(embedding)):
        embedding.append([0]*CONF.embedding_size)
    embedding = np.array(embedding)
    # print(total_hash_size, embedding.shape)
    return embedding
            

def build_model_columns():
    """Builds a set of wide and deep feature columns."""

    # Continuous columns
    continous_columns = [tf.feature_column.numeric_column('c{0}'.format(i)) for i in range(CONF.num_continous_feature)]

    # categorical columns
    categorical_columns = []
    hash_size = hash_size_of_cate_feature()
    for i in range(CONF.num_categorical_feature):
        categorical_columns.append(tf.feature_column.categorical_column_with_hash_bucket('d{0}'.format(i),
                                                            hash_bucket_size=hash_size[i]))
    # crossed-categorical columns
    crossed_columns = []
    for i in range(CONF.num_categorical_feature):
        for j in range(i+1, CONF.num_categorical_feature):
            crossed_columns.append(tf.feature_column.crossed_column(['d{0}'.format(i), 'd{0}'.format(j)], 
                                                                    hash_bucket_size=max(hash_size[i], hash_size[j])))
    
    # Wide columns and deep columns.
    wide_columns = categorical_columns + continous_columns # + crossed_columns
    deep_columns = [] #continous_columns
    if CONF.use_fm_vector:
        print('################### initialize embedding layer with FM latent vector ####################')
        fm_embedding = load_fm_embedding()
        curr = 0
        for i in range(CONF.num_categorical_feature):
            deep_columns.append(tf.feature_column.embedding_column(categorical_columns[i],
                                                                   dimension = CONF.embedding_size,
                                                                   initializer=tf.constant_initializer(fm_embedding[curr : curr + hash_size[i]])))
            curr += hash_size[i]
    else:
        deep_columns += [tf.feature_column.embedding_column(feature, dimension = CONF.embedding_size) 
                                for feature in categorical_columns]# + crossed_columns]
    return wide_columns, deep_columns
    # # Transformations.
    # age_buckets = tf.feature_column.bucketized_column(
    #     age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])


def build_estimator():
    """Build an estimator appropriate for the given model type."""
    wide_columns, deep_columns = build_model_columns()

    # Create a tf.estimator.RunConfig to ensure the model is run on CPU, which
    # trains faster than GPU for this model.
    run_config = tf.estimator.RunConfig().replace(
        session_config=tf.ConfigProto(device_count={'GPU': 0}))

    # optimizer with regularization
    wide_optimizer = tf.train.FtrlOptimizer(
                        learning_rate = CONF.learning_rate,
                        l1_regularization_strength = CONF.l1_regularization_strength,
                        l2_regularization_strength = CONF.l2_regularization_strength)
    deep_optimizer = tf.train.ProximalAdagradOptimizer(
                        learning_rate=CONF.learning_rate,
                        l1_regularization_strength = CONF.l1_regularization_strength,
                        l2_regularization_strength = CONF.l2_regularization_strength)

    if CONF.model_type == 'wide':
        return tf.estimator.LinearClassifier(
                model_dir=CONF.model_dir,
                feature_columns=wide_columns,
                optimizer=wide_optimizer,
                config=run_config)
    elif CONF.model_type == 'deep':
        return tf.estimator.DNNClassifier(
                model_dir=CONF.model_dir,
                feature_columns=deep_columns,
                hidden_units=CONF.hidden_units,
                # optimizer=deep_optimizer, # custom optimizer may not lead to good result
                dropout=CONF.drop_out,
                config=run_config)
    elif CONF.model_type == 'wdl':
        #return tf.estimator.DNNLinearCombinedClassifier(
        return  DNNLinearCombinedClassifier(
                model_dir=CONF.model_dir,
                linear_feature_columns=wide_columns,
                linear_optimizer=wide_optimizer,
                dnn_feature_columns=deep_columns,
                dnn_hidden_units=CONF.hidden_units,
                dnn_optimizer=deep_optimizer,
                dnn_dropout=CONF.drop_out,
                config=run_config)
    else:
        print('Error: unrecognized model type: {0}'.format(CONF.model_type))
        sys.exit()


def input_fn(data_file, num_epochs, shuffle, batch_size):
    """Generate an input function for the Estimator."""
    assert tf.gfile.Exists(data_file), (
        '%s not found. Please make sure you have run data_download.py and '
        'set the --data_dir argument to the correct path.' % data_file)

    def parse_csv(value):
        print('Parsing', data_file)
        columns = tf.decode_csv(value, record_defaults=_CSV_COLUMN_DEFAULTS)
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('label')
        return features, tf.equal(labels, 1)

    # Extract lines from input files using the Dataset API.
    dataset = tf.data.TextLineDataset(data_file)

    if shuffle:
        dataset = dataset.shuffle(buffer_size=CONF.num_train)

    dataset = dataset.map(parse_csv, num_parallel_calls=CONF.num_readers)

    # We call repeat after shuffling, rather than before, to prevent separate
    # epochs from blending together.
    dataset = dataset.repeat(num_epochs)
    dataset = dataset.batch(batch_size)
    return dataset


def export_model(model, model_type, export_dir):
    """Export to SavedModel format.

    Args:
    model: Estimator object
    model_type: string indicating model type. "wide", "deep" or "wide_deep"
    export_dir: directory to export the model.
    """
    wide_columns, deep_columns = build_model_columns()
    if model_type == 'wide':
        columns = wide_columns
    elif model_type == 'deep':
        columns = deep_columns
    else:
        columns = wide_columns + deep_columns
    feature_spec = tf.feature_column.make_parse_example_spec(columns)
    example_input_fn = (
        tf.estimator.export.build_parsing_serving_input_receiver_fn(feature_spec))
    model.export_savedmodel(export_dir, example_input_fn)


def run_wide_deep():
    """Run Wide-Deep training and eval loop."""

    # Clean up the model directory if present
    shutil.rmtree(CONF.model_dir, ignore_errors=True)
    
    model = build_estimator()
    global_step = 0
    model_name = model.latest_checkpoint()
    if model_name:
        global_step = int(model_name.split('/')[-1].split('-')[1])
        print('restoring from glbal step {0}'.format(global_step))
    start_epoch = (global_step * CONF.batch_size) // CONF.num_train
    # Train and evaluate the model every `flags.epochs_between_evals` epochs.
    def train_input_fn():
        return input_fn(CONF.train_file, CONF.epochs_between_evals, True, CONF.batch_size)

    def eval_train_input_fn():
        return input_fn(CONF.train_file, 1, False, CONF.batch_size)

    def eval_val_input_fn():
        return input_fn(CONF.val_file, 1, False, CONF.batch_size)

    def calculate_auc(y, pred):
        fpr, tpr, thresholds = metrics.roc_curve(y, pred)
        return metrics.auc(fpr, tpr)

    def get_label():
        train_labels, val_labels = [], []
        with open(CONF.train_file, mode='r', encoding='utf8') as rf:
            for line in rf:
                blocks = line.rstrip('\n').split(',') # line.strip().split('\t) will cause error
                train_labels.append(int(blocks[0]))
        with open(CONF.val_file, mode='r', encoding='utf8') as rf:
            for line in rf:
                blocks = line.rstrip('\n').split(',') # line.strip().split('\t) will cause error
                val_labels.append(int(blocks[0]))
        assert len(train_labels) == CONF.num_train and len(val_labels) == CONF.num_val, 'number of labels and samples not equal'
        return train_labels, val_labels
    
    def write_log(title, content):
        file_path = './logs/{0}.log'.format(title)
        if not os.path.exists(file_path):
            with open(file_path, mode = 'w', encoding = 'utf8') as wf:
                wf.write('\ttrain_log_loss\tval_log_loss\ttrain_auc\tval_auc\n')
        with open(file_path, mode = 'a', encoding='utf8') as wf:
            wf.write(content)
        
    # visualization for train and validation
    if CONF.visualize:
        vis = visdom.Visdom(env=CONF.env)
    train_loss, train_auc = [], []
    val_loss, val_auc = [], []
    train_labels, val_labels = get_label()

    for n in range(CONF.epochs // CONF.epochs_between_evals):
        model.train(input_fn=train_input_fn)
        # train_results = model.evaluate(input_fn=eval_train_input_fn)
        # val_results = model.evaluate(input_fn=eval_val_input_fn)
        train_predict_prob = [p['logistic'][0] for p in model.predict(input_fn=eval_train_input_fn)]
        val_predict_prob = [p['logistic'][0] for p in model.predict(input_fn=eval_val_input_fn)]

        if CONF.visualize:
            train_loss.append(metrics.log_loss(train_labels, train_predict_prob))
            train_auc.append(calculate_auc(train_labels, train_predict_prob))
            val_loss.append(metrics.log_loss(val_labels, val_predict_prob))
            val_auc.append(calculate_auc(val_labels, val_predict_prob))
            
            title = '{13}_{0}train_{1}val_{2}epochs_{3}bs_{4}lr_{5}hs_{6}emb_{7}hidden_{8}dropout_{9}L1_{10}L2_FMEmbedding({11})_{12}'.format(
                    CONF.num_train,
                    CONF.num_val,
                    CONF.epochs,
                    CONF.batch_size,
                    CONF.learning_rate,
                    CONF.max_hash_size,
                    CONF.embedding_size,
                    CONF.hidden_units,
                    CONF.drop_out,
                    CONF.l1_regularization_strength,
                    CONF.l2_regularization_strength,
                    CONF.use_fm_vector,
                    CONF.loss_fn,
                    CONF.model_type)
            content = '[{0}]Epoch {1} :{2}\t {3}\t {4}\t {5}\n'.format(strftime("%m-%d %H:%M", gmtime()),
                                                                       start_epoch+(n+1)*CONF.epochs_between_evals,
                                                                       train_loss[-1],
                                                                       val_loss[-1],
                                                                       train_auc[-1],
                                                                       val_auc[-1])
            write_log(title, content)

            x_epoch = [start_epoch+i*CONF.epochs_between_evals for i in range(1, n+2)]
            t_auc = dict(x=x_epoch, y=train_auc, type='custom', name='train_auc')
            v_auc = dict(x=x_epoch, y=val_auc, type='custom', name='val_auc')
            t_loss = dict(x=x_epoch, y=train_loss, type='custom', name='train_loss')
            v_loss = dict(x=x_epoch, y=val_loss, type='custom', name='val_loss')
            layout=dict(title=title, xaxis={'title':'epochs'}, yaxis={'title':'LogLoss_AUC'})
            data = [t_loss, v_loss, t_auc, v_auc]
            vis._send({'data':data, 'layout':layout, 'win':title})


        # Display evaluation metrics
        # tf.logging.info('Results at epoch %d / %d',
        #                 (n + 1) * CONF.epochs_between_evals,
        #                 CONF.epochs)
        # tf.logging.info('-' * 60)

        # for key in sorted(val_results):
        #     tf.logging.info('%s: %s' % (key, val_results[key]))

        # Export the model
        if CONF.model_dir is not None:
            export_model(model, CONF.model_type, CONF.model_dir)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    fire.Fire()