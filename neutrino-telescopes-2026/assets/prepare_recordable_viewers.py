"""Refresh local recordable DN event viewers without publishing result arrays.

This uses existing results, not a new transport computation. Public lecture
assets contain only exported movies; these JSON/HTML companions remain local
under LightHit's ignored .build directory.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tomllib
import numpy as np

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
sys.path.insert(0,str(WORKSPACE/'lighthit/src'))
from lighthit.viewer import validate_event_viewer,write_event_viewer,source_timing


def restored_axis_timing(event,cfg):
    """Recover display timing from the exact stored source/pose contract.

    This only describes the source head. The detector arrival bins, charges
    and reference times are not recalculated or altered.
    """
    from lighthit.experimental.g4_source import SourceContract,load_event
    summary=event['source_summary']; pose=event['pose']
    file=WORKSPACE/'lighthit/g4_data'/Path(summary['file']).name
    contract=SourceContract(**{key:summary['contract'][key] for key in ('phase_index','wavelength_low_nm','wavelength_high_nm')})
    elements=load_event(file,summary['event'],contract).moved(rotation=pose['rotation'],translation=pose['translation_m'])
    if len(elements)!=summary['elements']: raise ValueError('Stored source element count differs; do not invent a clock')
    tol=cfg['timing']
    np.testing.assert_allclose(elements.photons.sum(),summary['photons'],rtol=tol['validation_rtol'],atol=tol['validation_atol'])
    np.testing.assert_allclose(elements.centroid_m,summary['centroid_m'],rtol=tol['validation_rtol'],atol=tol['validation_atol'])
    source=event['sources'][0]
    timing=source_timing(elements,source['position_m'],source['direction'],source['extent_m'],bins=tol['bins'])
    if timing is None: raise ValueError('The original source cannot supply an axial timing fit')
    return timing


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=HERE/'viewer_recording.toml')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    cfg=tomllib.loads(args.config.read_text())
    output=(args.output or WORKSPACE/cfg['paths']['local_output']).resolve()
    public_roots=(HERE.parent.resolve(),HERE.parents[1]/'_site')
    if any(output.is_relative_to(root) for root in public_roots):
        parser.error('Raw event viewers must stay outside the public lecture tree; export only movies')
    output.mkdir(parents=True,exist_ok=True)
    report={'movies_only_for_publication':True,'events':[]}
    for kind,entry in cfg['events'].items():
        source=args.input or WORKSPACE/entry.get('input',cfg['paths']['input'])
        original=json.loads(source.read_text()); validate_event_viewer(original)
        found=[e for e in original['events'] if e['event_id']==entry['event_id']]
        if len(found)!=1: parser.error(f"Expected exactly one source event: {entry['event_id']}")
        payload=copy.deepcopy(original); payload['events']=[copy.deepcopy(found[0])]
        event=payload['events'][0]; event['label']=entry['label']
        for description in event.get('sources',[]): description['label']=entry['label']
        if entry.get('restore_source_timing'):
            event['sources'][0]['timing']=restored_axis_timing(event,cfg)
        # English labels are display-only; physics arrays and their signs remain exact.
        for key in ('components','charge_components','time_origin_ns','active'):
            if key in found[0]: np.testing.assert_array_equal(np.asarray(event[key]),np.asarray(found[0][key]))
        validate_event_viewer(payload)
        path=write_event_viewer(payload,output/f'{kind}.html')
        if cfg['recording']['presentation_default']:
            html=path.read_text().replace('<body>','<body class="presentation-view">').replace('id="presentation" type="checkbox"','id="presentation" type="checkbox" checked')
            path.write_text(html)
        report['events'].append({'kind':kind,'event_id':entry['event_id'],'html':path.name,'label':entry['label'],
                                 'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        print(path)
    (output/'provenance.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
