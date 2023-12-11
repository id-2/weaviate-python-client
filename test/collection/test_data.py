from unittest.mock import Mock

import pytest

from weaviate.collections.data import _DataCollection
from weaviate.connect import Connection


@pytest.fixture
def mock_connection():
    mock = Mock(spec=Connection)
    mock.server_version = "1.0.0"
    return mock


@pytest.fixture
def data(mock_connection: Connection):
    return _DataCollection(mock_connection, "Dummy", None, None)


def test_delete_by_id_wrong_parameter_type(data: _DataCollection):
    with pytest.raises(TypeError) as e:
        data.delete_by_id(1)
    assert (
        e.value.args[0]
        == "Argument 'uuid' must be typing.Union[str, uuid.UUID], but got <class 'int'>"
    )


def test_delete_by_id_extra_positional_parameter(data: _DataCollection):
    with pytest.raises(TypeError) as e:
        data.delete_by_id("1", "extra")
    assert e.value.args[0] == "too many positional arguments"


def test_delete_by_id_extra_keyword_parameter(data: _DataCollection):
    with pytest.raises(TypeError) as e:
        data.delete_by_id("1", extra="extra")
    assert e.value.args[0] == "got an unexpected keyword argument 'extra'"
