"""Mockup profiles (.mockup.json): creation, keeping user changes, groups and migration from Mockup Studio."""
import os


def analysis(**over):
    obj = {'uid': 'u1', 'name': 'Design (double-click)', 'inner': [1000, 500], 'aspect': 2.0, 'ratio': '2:1',
           'surface': 0.2, 'coverage': 0.05, 'withBackground': False, 'sample': 0.95, 'logo': 'light', 'visible': True}
    obj.update(over)
    return {'size': [4000, 3000], 'objects': [obj]}


def test_profile_with_what_was_detected(server):
    p = server.build_profile('/x/Mockup Gallery/Outdoor/A.psd', analysis())
    o = p['objects'][0]
    assert p['group'] == 'Other' and o['ratio'] == '2:1'   # outside the gallery → Other
    assert (o['logo'], o['background'], o['fit']) == ('light', 'transparent', 'contain')


def test_full_bleed_design_covers_the_canvas(server):
    o = server.build_profile('/x/A.psd', analysis(withBackground=True, logo='original'))['objects'][0]
    assert (o['background'], o['fit'], o['logo']) == ('full-bleed', 'cover', 'original')


def test_reanalyzing_keeps_user_changes(server):
    prev = server.build_profile('/x/A.psd', analysis(), name='My mockup')
    prev['group'] = 'Merchandise'
    prev['objects'][0].update(logo='dark', fit='stretch', rotate=90)
    again = server.build_profile('/x/A.psd', analysis(surface=0.9, logo='dark'), previous=prev)
    o = again['objects'][0]
    assert again['name'] == 'My mockup' and again['group'] == 'Merchandise'
    assert (o['logo'], o['fit'], o['rotate']) == ('dark', 'stretch', 90)


def test_profile_values_reach_the_metadata(server):
    objs = server.objects_from_profile(server.build_profile('/x/A.psd', analysis()))
    assert objs[0]['tint'] == '#ffffff' and objs[0]['fit'] == 'contain' and objs[0]['background'] == 'transparent'


def _psd_in(server, group, name):
    folder = os.path.join(server.GALLERY, group)
    os.makedirs(folder, exist_ok=True)
    psd = os.path.join(folder, name)
    open(psd, 'wb').write(b'content does not matter')
    profile = server.build_profile(psd, analysis())
    server.write_json(server.profile_path(psd), profile)
    return psd, server.write_meta(psd, profile)


def test_changing_the_group_moves_the_psd_and_its_profile(server):
    psd, meta = _psd_in(server, 'Other', 'Move.psd')
    new = server.update_profile(meta, {'group': 'Outdoor', 'objects': [{'id': 'u1', 'logo': 'dark'}]})
    dest = os.path.join(server.GALLERY, 'Outdoor', 'Move.psd')
    assert os.path.exists(dest) and not os.path.exists(psd)
    assert os.path.exists(server.profile_path(dest)) and not os.path.exists(server.profile_path(psd))
    assert new['category'] == 'Outdoor' and new['id'] == meta['id']
    assert new['smartObjects'][0]['tint'] == '#1c2030'


def test_new_groups_and_valid_names(server):
    assert server.clean_group('  Shop windows / stores ') == 'Shop windows   stores'
    assert server.clean_group('../..') is None and server.clean_group('') is None
    os.makedirs(os.path.join(server.GALLERY, 'Packaging'), exist_ok=True)
    assert server.groups()[:3] == ['Outdoor', 'Merchandise', 'Other'] and 'Packaging' in server.groups()


def test_moving_to_a_new_group_creates_the_folder(server):
    _, meta = _psd_in(server, 'Other', 'New.psd')
    new = server.update_profile(meta, {'group': 'Trade shows'})
    assert new['category'] == 'Trade shows' and os.path.exists(os.path.join(server.GALLERY, 'Trade shows', 'New.psd'))
    assert 'Trade shows' in server.groups()


def test_profile_stores_details_and_layers(server):
    a = analysis(warp='cylinder', perspective='perspective', instances=[{'name': 'x', 'filters': ['Gaussian Blur 3 px']}])
    a['layers'] = [{'name': 'Background', 'type': 'Pixels'}]
    p = server.build_profile('/x/A.psd', a)
    assert p['format'] == server.PROFILE_FORMAT and p['layers'][0]['name'] == 'Background'
    assert p['objects'][0]['warp'] == 'cylinder' and p['objects'][0]['instances'][0]['filters']


def test_mockup_studio_profile_is_converted_keeping_user_changes(server, monkeypatch):
    psd = os.path.join(server.GALLERY, 'Other', 'Studio.psd')
    os.makedirs(os.path.dirname(psd), exist_ok=True)
    open(psd, 'wb').write(b'x')
    server.write_json(server.profile_path(psd), {
        'formato': 2, 'nombre': 'Shop', 'grupo': 'Merchandising', 'creado': '2026-01-01T00:00:00',
        'objetos': [{'id': 'u1', 'nombre': 'Logo', 'logo': 'oscuro', 'fondo': 'con fondo', 'ajuste': 'stretch', 'giro': 90}]})
    monkeypatch.setattr(server.engine, 'analyze', lambda p: analysis())
    monkeypatch.setattr(server.engine, 'preview', lambda p: __import__('PIL.Image').Image.new('RGB', (4, 4)))
    meta = server.register_mockup(psd, reanalyze=False)
    p = server.read_json(server.profile_path(psd), {})
    o = p['objects'][0]
    assert p['format'] == 1 and p['name'] == 'Shop' and p['group'] == 'Merchandise' and p['created'].startswith('2026-01')
    assert (o['logo'], o['background'], o['fit'], o['rotate']) == ('dark', 'full-bleed', 'stretch', 90)
    assert meta['category'] == 'Merchandise' and meta['smartObjects'][0]['background'] == 'full-bleed'


def test_mockup_studio_folders_are_migrated_on_startup(server):
    """conftest.py leaves a Mockup Studio work folder: app.py renames it when imported."""
    root = server.ROOT
    assert not os.path.exists(os.path.join(root, 'Galería de mockups')) and not os.path.exists(os.path.join(root, 'Flujos'))
    assert os.path.exists(os.path.join(server.GALLERY, 'Outdoor', 'Old.psd'))
    assert os.path.exists(os.path.join(server.FLOWS, 'Mine.mwf'))
    meta = server.read_json(os.path.join(server.MOCKUPS, 'old-111111.json'), {})
    assert meta['path'] == os.path.join('Mockup Gallery', 'Outdoor', 'Old.psd') and meta['category'] == 'Outdoor'
    assert meta['profilePath'] == os.path.join('Mockup Gallery', 'Outdoor', 'Old.mockup.json')
    assert 'Flujos' not in str(server.read_json(server.WORKFLOW, {}))   # the open workflow points to Flows/
