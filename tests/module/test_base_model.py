from sknlp.module.base_model import BaseNLPModel


def test_build_vocab():
    texts = ['11111', '222', '33333']
    vocab = BaseNLPModel.build_vocab(texts, list, min_frequency=4)
    assert '1' in vocab
    assert '2' not in vocab


class TestBaseNLPModel:

    name = "xx"
    max_length = 100
    model = BaseNLPModel(max_length=max_length, name=name)

    def test_get_config(self):
        config = self.model.get_config()
        assert config["max_length"] == self.max_length
        assert config["name"] == self.name
