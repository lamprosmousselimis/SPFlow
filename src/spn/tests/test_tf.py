'''
Created on March 28, 2018

@author: Alejandro Molina
'''
import numpy as np
from joblib import Memory

from spn.algorithms.Inference import log_likelihood
from spn.algorithms.StructureLearning import learn_structure
from spn.algorithms.splitting.KMeans import split_rows_KMeans
from spn.algorithms.splitting.RDC import split_cols_RDC
from spn.gpu.TensorFlow import eval_tf
from spn.leaves.Histograms import histogram_likelihood, add_domains, create_histogram_leaf
from spn.structure.Base import Context

memory = Memory(cachedir="cache", verbose=0, compress=9)


@memory.cache
def learn(data, ds_context):
    spn = learn_structure(data, ds_context, split_rows_KMeans, split_cols_RDC, create_histogram_leaf)

    return spn


if __name__ == '__main__':
    data = np.loadtxt("test_data.txt", delimiter=";", dtype=np.int32)

    ds_context = Context()
    ds_context.statistical_type = np.asarray(["discrete"] * data.shape[1])
    add_domains(data, ds_context)

    spn = learn(data, ds_context)
    py_ll = log_likelihood(spn, data, histogram_likelihood)

    tf_out, time = eval_tf(spn, data, log_space=False, save_graph_path='tfgraph', trace=True)
    tf_out, time = eval_tf(spn, data, log_space=False, save_graph_path='tfgraph', trace=True)
    tf_out_log, time2 = eval_tf(spn, data, log_space=True, save_graph_path='tfgraph')

    print("results are similar for TF and Python?", np.all(np.isclose(py_ll - np.log(tf_out), 0)))
    print("time in ns", time)
    print("results are similar for Log TF and Python?", np.all(np.isclose(py_ll - tf_out_log, 0)))
