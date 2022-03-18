import os
from typing import Type

import pytest

from daemon.models import DaemonID, DeploymentModel, PodModel
from daemon.stores import DeploymentStore, PodStore
from daemon.stores.partial import PartialStore
from jina import Executor

cur_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='module')
def workspace():
    from tests.conftest import _clean_up_workspace, _create_workspace_directly

    image_id, network_id, workspace_id, workspace_store = _create_workspace_directly(
        cur_dir
    )
    yield workspace_id
    _clean_up_workspace(image_id, network_id, workspace_id, workspace_store)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'model, store, id',
    [
        (PodModel(), PodStore, DaemonID(f'jpod')),
        # (PodModel(), PodStore, DaemonID(f'jpod')),
    ],
)
async def test_podpod_store_add(model, store, id, workspace):
    s = store()
    await s.add(id=id, params=model, workspace_id=workspace, ports={})
    assert len(s) == 1
    assert id in s
    await s.delete(id)
    assert not s


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'model, store, type',
    [
        (PodModel(), PodStore, 'pod'),
        # (PodModel(), PodStore, 'pod')
    ],
)
async def test_podpod_store_multi_add(model, store, type, workspace):
    s = store()
    for j in range(5):
        id = DaemonID(f'j{type}')
        await s.add(id=id, params=model, workspace_id=workspace, ports={})

        assert len(s) == j + 1
        assert id in s
    await s.clear()
    assert not s


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'model, store, id',
    [
        (PodModel(), PodStore, DaemonID(f'jpod')),
        # (PodModel(), PodStore, DaemonID(f'jpod')),
    ],
)
async def test_podpod_store_add_bad(model, store, id, workspace):
    class BadCrafter(Executor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise NotImplementedError

    model.uses = 'BadCrafter'
    s = store()
    with pytest.raises(Exception):
        await s.add(id=id, params=model, workspace_id=workspace, ports={})
    assert not s
