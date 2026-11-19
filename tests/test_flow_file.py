""".mwf format: export and import workflows."""
import io
import os
import xml.etree.ElementTree as ET

import pytest
from PIL import Image


def fake_mockup(server, mid='test-abc123', name='Test', file='Test.psd', uids=('u1', 'u2')):
    meta = {'id': mid, 'name': name, 'file': file, 'path': f'Mockup Gallery/Other/{file}', 'category': 'Other',
            'size': [100, 100], 'added': 0,
            'smartObjects': [{'uid': u, 'name': u, 'inner': [10, 10], 'visible': True, 'fit': 'contain', 'tint': None,
                              'rotate': 0} for u in uids]}
    server.write_json(os.path.join(server.MOCKUPS, mid + '.json'), meta)
    return meta


def new_design(server, png, color=(255, 255, 255, 255)):
    return server.save_design(Image.open(io.BytesIO(png(color=color))), f'logo-{color[0]}.png')


def test_round_trip_with_several_designs(server, png):
    m = fake_mockup(server)
    d1, d2 = new_design(server, png), new_design(server, png, (10, 20, 30, 255))
    state = {'title': 'Campaign', 'output': {'format': 'jpg', 'scale': 0.5}, 'exportPos': {'x': 900, 'y': 30},
             'designNodes': [{'id': 'd1', 'design': d1, 'x': 10, 'y': 20}, {'id': 'd2', 'design': d2, 'x': 10, 'y': 500}],
             'nodes': [{'id': 'n1', 'mockupId': m['id'], 'x': 470, 'y': 56, 'links': {
                 'u1': {'design': 'd1', 'fit': 'cover', 'tint': '#1c2030', 'rotate': 90},
                 'u2': {'design': 'd2', 'fit': 'contain', 'tint': None, 'rotate': 0}}}]}
    xml = server.flow_to_xml(state)
    root = ET.fromstring(xml)
    assert root.tag == 'mockupWorkflow' and root.get('version') == server.FLOW_FORMAT == '1'
    # paths of the files used
    designs = root.find('designs').findall('design')
    assert [os.path.basename(d.get('path')) for d in designs] == [d1['id'] + '.png', d2['id'] + '.png']
    assert root.find('mockups/mockup').get('path').endswith('Test.psd')
    back = server.xml_to_flow(xml)
    assert back['title'] == 'Campaign' and back['output'] == {'format': 'jpg', 'scale': 0.5}
    assert [d['design']['id'] for d in back['designNodes']] == [d1['id'], d2['id']]   # designs are not duplicated
    links = back['nodes'][0]['links']
    assert links['u1'] == {'design': 'd1', 'fit': 'cover', 'tint': '#1c2030', 'rotate': 90}
    assert links['u2']['design'] == 'd2' and back['missing'] == []


def test_finds_the_mockup_by_file_name_if_the_id_changes(server):
    m = fake_mockup(server, mid='other-111111', name='Shop window', file='Shop window.psd')
    xml = server.flow_to_xml({'title': 't', 'nodes': [{'id': 'n1', 'mockupId': m['id'], 'links': {}}]})
    xml = xml.replace(b'id="other-111111"', b'id="unknown"')
    assert server.xml_to_flow(xml)['nodes'][0]['mockupId'] == m['id']


def test_loads_the_design_from_its_path_if_not_embedded(server, png, tmp_path):
    p = tmp_path / 'external.png'
    p.write_bytes(png(color=(200, 10, 10, 255)))
    xml = f'<mockupWorkflow version="1"><designs><design node="d1" name="external.png" source="{p}"/></designs></mockupWorkflow>'
    d = server.xml_to_flow(xml.encode())['designNodes'][0]['design']
    assert d and d['source'] == str(p)


def test_reports_missing_mockups(server):
    xml = b'<?xml version="1.0"?><mockupWorkflow version="1"><title>x</title><mockups>' \
          b'<mockup id="missing" name="Ghost" file="Ghost.psd" path="/does/not/exist/Ghost.psd"/></mockups></mockupWorkflow>'
    back = server.xml_to_flow(xml)
    assert back['nodes'] == [] and back['missing'] == ['Ghost']


@pytest.mark.parametrize('data', [b'not xml', b'<?xml version="1.0"?><somethingElse/>',
                                  b'<mockupStudioFlow version="2"/>'])
def test_rejects_files_that_are_not_workflows(server, data):
    with pytest.raises(ValueError):
        server.xml_to_flow(data)


def test_link_to_a_missing_object_is_dropped(server):
    m = fake_mockup(server, mid='so-222222', file='SO.psd')
    xml = server.flow_to_xml({'title': 't', 'designNodes': [{'id': 'd1', 'design': None}],
                              'nodes': [{'id': 'n1', 'mockupId': m['id'], 'links': {'deleted': {'design': 'd1'}}}]})
    assert server.xml_to_flow(xml)['nodes'][0]['links'] == {}


def test_node_labels(server, png):
    m = fake_mockup(server, mid='lbl-555555', file='Lbl.psd')
    d = new_design(server, png)
    xml = server.flow_to_xml({'title': 't', 'designNodes': [{'id': 'd1', 'label': 'Main logo', 'design': d}],
                              'nodes': [{'id': 'n1', 'label': 'Downtown shop window', 'mockupId': m['id'], 'links': {}}]})
    back = server.xml_to_flow(xml)
    assert back['designNodes'][0]['label'] == 'Main logo'
    assert back['nodes'][0]['label'] == 'Downtown shop window'
