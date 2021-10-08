import pytest

import tensorflow as tf
from tensorflow.python.tools import saved_model_utils
import numpy as np
from .bert2vec import Bert2vec, BertFamily


@pytest.fixture
def inputs():
    token_ids = tf.constant([[101, 3432, 324, 123, 102], [101, 444, 222, 102, 0]])
    type_ids = tf.zeros_like(token_ids)
    mask = tf.constant([[1, 1, 1, 1, 1], [1, 1, 1, 1, 0]])
    attention_mask = mask[..., None] * mask[:, None, :]
    logits_mask = tf.constant([[0, 0, 1, 1, 0], [0, 1, 0, 0, 0]])
    return [token_ids, type_ids, attention_mask, logits_mask]


def test_from_bert_checkpoint():
    Bert2vec.from_tfv1_checkpoint(BertFamily.BERT, "data/bert_3l")


def test_from_albert_checkpoint():
    Bert2vec.from_tfv1_checkpoint(BertFamily.ALBERT, "data/albert_tiny_zh_google")


def test_from_electra_checkpoint():
    Bert2vec.from_tfv1_checkpoint(BertFamily.ELECTRA, "data/electra_180g_small")


def test_bert2vec(inputs):
    bv = Bert2vec.from_tfv1_checkpoint(BertFamily.BERT, "data/bert_3l")
    outputs = bv(inputs[:3])
    assert len(outputs) == 4
    assert outputs[0].ndim == 2
    assert outputs[1].ndim == 3
    assert outputs[2].shape[1] == 5

    bv.return_all_layer_outputs = True
    outputs = bv(inputs[:3], logits_mask=inputs[3])
    assert len(outputs) == 4
    assert outputs[0].ndim == 2
    assert outputs[1][-1].ndim == 3
    assert outputs[2].shape[1] == 2


def test_bert2vec_save_load(tmp_path, inputs):
    bv = Bert2vec.from_tfv1_checkpoint(BertFamily.ELECTRA, "data/electra_180g_small")
    outputs = bv(inputs[:3])
    bv.save(str(tmp_path))
    new_bv = Bert2vec.load(str(tmp_path))
    new_outputs = new_bv(inputs[:3])
    np.testing.assert_array_almost_equal(
        outputs[1].numpy(), new_outputs[1].numpy(), decimal=3
    )


def test_bert2vec_save_load_archive(tmp_path, inputs):
    bv = Bert2vec.from_tfv1_checkpoint(BertFamily.ELECTRA, "data/electra_180g_small")
    outputs = bv(inputs[:3])
    filename = tmp_path / "archive.tar"
    bv.save_archive(str(filename))
    new_bv = Bert2vec.load_archive(str(filename))
    new_outputs = new_bv(inputs[:3])
    np.testing.assert_array_almost_equal(
        outputs[1].numpy(), new_outputs[1].numpy(), decimal=3
    )


def test_bert2vec_export(tmp_path):
    bv = Bert2vec.from_tfv1_checkpoint(BertFamily.ELECTRA, "data/electra_180g_small")
    bv.export(str(tmp_path), "bert2vec")
    directory = tmp_path / "bert2vec" / "0"
    meta_graph_def = saved_model_utils.get_meta_graph_def(str(directory), "serve")
    outputs = meta_graph_def.signature_def["serving_default"].outputs
    assert len(outputs) == 2
    assert len(outputs[bv._inference_kwargs["output_names"][0]].tensor_shape.dim) == 2
    assert len(outputs[bv._inference_kwargs["output_names"][1]].tensor_shape.dim) == 3


def test_bert2vec_export_cls(tmp_path):
    bv = Bert2vec.from_tfv1_checkpoint(BertFamily.ELECTRA, "data/electra_180g_small")
    bv.export(str(tmp_path), "bert2vec", only_output_cls=True)
    directory = tmp_path / "bert2vec" / "0"
    meta_graph_def = saved_model_utils.get_meta_graph_def(str(directory), "serve")
    outputs = meta_graph_def.signature_def["serving_default"].outputs
    assert len(outputs) == 1
    assert len(outputs[bv._inference_kwargs["output_names"][0]].tensor_shape.dim) == 2