"""HTTP API of the local server."""
import io
import os


def test_about(client):
    from version import FLOW_FORMAT, __version__
    r = client.get('/api/about').get_json()
    assert r['version'] == __version__ and r['license'] == 'MIT' and r['author']
    assert r['name'] == 'Mockup Workflow' and r['flowFormat'] == FLOW_FORMAT and r['flowExt'] == '.mwf'


def test_interface_is_served(client):
    r = client.get('/')
    assert r.status_code == 200 and b'Mockup Workflow' in r.data


def test_upload_design_and_list_it(client, png):
    r = client.post('/api/designs', data={'file': (io.BytesIO(png()), 'logo.png')}, content_type='multipart/form-data')
    d = r.get_json()
    assert r.status_code == 200 and d['transparent'] and d['width'] == 64
    assert any(x['id'] == d['id'] for x in client.get('/api/designs').get_json())
    assert client.get(f'/api/designs/{d["id"]}.png').status_code == 200


def test_rejects_a_design_that_is_not_an_image(client):
    r = client.post('/api/designs', data={'file': (io.BytesIO(b'hello'), 'x.png')}, content_type='multipart/form-data')
    assert r.status_code == 400 and 'image' in r.get_json()['error']


def test_rejects_a_psd_that_is_not_a_psd(client):
    r = client.post('/api/mockups', data={'file': (io.BytesIO(b'hello'), 'x.txt')}, content_type='multipart/form-data')
    assert r.status_code == 400


def test_workflow_autosave(client):
    client.put('/api/workflow', json={'title': 'Draft', 'nodes': []})
    wf = client.get('/api/workflow').get_json()
    assert wf['title'] == 'Draft' and wf['savedAt']


def test_run_without_linked_design_explains_the_error(client, server):
    server.write_json(os.path.join(server.MOCKUPS, 'run-444444.json'), {
        'id': 'run-444444', 'name': 'No links', 'file': 'x.psd', 'path': 'x.psd', 'category': 'Other',
        'size': [1, 1], 'smartObjects': [{'uid': 'u1', 'name': 'u1'}]})
    r = client.post('/api/runs', json={'nodes': [{'mockupId': 'run-444444', 'links': [{'uid': 'u1', 'designId': 'none'}]}]})
    assert r.status_code == 400 and 'design' in r.get_json()['error']


def test_export_and_import_mwf_over_http(client, png):
    d = client.post('/api/designs', data={'file': (io.BytesIO(png()), 'logo.png')}, content_type='multipart/form-data').get_json()
    r = client.post('/api/flows/export', json={'title': 'Odd / flow', 'designNodes': [{'id': 'd1', 'design': d}], 'nodes': []})
    assert r.status_code == 200 and r.headers['X-File-Name'].endswith('.mwf')
    back = client.post('/api/flows/import', data=r.data, content_type='application/xml').get_json()
    assert back['title'] == 'Odd / flow' and back['designNodes'][0]['design']['id'] == d['id']


def test_flow_file_names(server):
    assert server.flow_file_name('Campaign') == 'Campaign.mwf' and server.flow_file_name('Campaign.mwf') == 'Campaign.mwf'
    assert server.flow_file_name('a/b') == 'a-b.mwf' and server.flow_file_name('') == 'Workflow.mwf'


def test_demo_workflow(client, server):
    st = client.post('/api/demo').get_json()
    assert st['title'] == 'Demo' and st['fileName'] == 'Demo.mwf'
    d = st['designNodes'][0]['design']
    assert d['name'] == 'demo.png' and d['transparent']
    assert st['designNodes'][1]['label'] == 'MW monogram'
    mono = st['designNodes'][1]['design']
    assert mono['name'].endswith('.svg') and mono['source'].endswith('.svg') and os.path.exists(mono['source'])
    assert os.path.exists(os.path.join(server.FLOWS, 'Demo.mwf'))
    again = client.post('/api/demo').get_json()
    assert again['designNodes'][0]['design']['id'] == d['id']     # the design is not duplicated


def test_recent_designs_remove_and_demo_fallback(client, server):
    for f in os.listdir(server.DESIGNS):           # no visible designs → the demo
        if f.endswith('.json'):
            m = server.read_json(os.path.join(server.DESIGNS, f), {})
            m['hidden'] = True
            server.write_json(os.path.join(server.DESIGNS, f), m)
    lst = client.get('/api/designs').get_json()
    assert [d['name'] for d in lst] == ['demo.png', 'demo.svg'] and all(d.get('demo') for d in lst)
    assert lst[1]['source'].endswith('demo.svg')
    up = client.post('/api/designs', data={'file': (io.BytesIO(_png((9, 9, 9, 255))), 'mine.png')},
                     content_type='multipart/form-data').get_json()
    lst = client.get('/api/designs').get_json()
    assert lst[0]['id'] == up['id'] and not any(d.get('demo') for d in lst)
    client.patch(f"/api/designs/{up['id']}", json={'hidden': True})
    assert all(d['id'] != up['id'] for d in client.get('/api/designs').get_json())


def test_clear_history(client, server):
    server.write_json(server.RUNS_DB, [{'id': 'r1', 'status': 'success', 'steps': []}])
    os.makedirs(os.path.join(server.RUNS, 'r1'), exist_ok=True)
    trash = []
    orig = server.move_to_trash
    server.move_to_trash = lambda p: trash.append(p)
    try:
        r = client.delete('/api/runs').get_json()
    finally:
        server.move_to_trash = orig
    assert r['removed'] == 1 and client.get('/api/runs').get_json() == [] and trash


def _png(color):
    from conftest import png_bytes
    return png_bytes(color=color)


def test_old_demo_designs_are_replaced(client, server):
    from PIL import Image
    old = server.save_design(Image.new('RGBA', (8, 8), (250, 200, 0, 255)), 'demo.svg')   # the old "MS" monogram
    server.write_json(server.WORKFLOW, {'title': 'Flujo sin título', 'designNodes': [
        {'id': 'd2', 'label': 'Monograma MS', 'design': old}]})
    server.retire_old_demo()
    wf = server.read_json(server.WORKFLOW, {})
    dn = wf['designNodes'][0]
    assert wf['title'] == 'Untitled workflow' and dn['label'] == 'MW monogram'
    assert dn['design']['id'] != old['id'] and dn['design']['name'] == 'demo.svg'
    assert server.read_json(os.path.join(server.DESIGNS, old['id'] + '.json'), {})['hidden']
