"""A source clock is restored only when its recorded contract agrees."""
import copy
import unittest
from unittest.mock import patch
import numpy as np
from prepare_recordable_viewers import restored_axis_timing
from lighthit.experimental.g4_source import LightElements,SourceContract


class SourceTimingTest(unittest.TestCase):
    def fixture(self):
        contract=SourceContract()
        start=np.column_stack([np.zeros(4),np.zeros(4),np.arange(4)-2])
        elements=LightElements(start,np.tile([0.,0.,1.],(4,1)),np.ones(4),np.ones(4),np.full(4,1/contract.phase_index),
            np.arange(4)*4.,(np.arange(4)+1)*4.,np.arange(4),np.ones(4,dtype=int),contract,{})
        event={'source_summary':{'file':'fixture.h5','event':0,'contract':contract.as_dict(),'elements':4,'photons':4.,'centroid_m':[0.,0.,0.]},
            'pose':{'rotation':np.eye(3).tolist(),'translation_m':[0.,0.,0.]},
            'sources':[{'position_m':[0.,0.,0.],'direction':[0.,0.,1.],'extent_m':2.}]}
        cfg={'timing':{'bins':16,'validation_rtol':1e-10,'validation_atol':1e-8}}
        return elements,event,cfg

    def test_clock_is_monotonic_without_mutating_input_metadata(self):
        elements,event,cfg=self.fixture(); before=copy.deepcopy(event)
        with patch('lighthit.experimental.g4_source.load_event',return_value=elements):
            timing=restored_axis_timing(event,cfg)
        self.assertEqual(event,before)
        self.assertEqual(len(timing['s_m']),cfg['timing']['bins'])
        self.assertTrue(np.all(np.diff(timing['t_ns'])>0))

    def test_mismatched_source_yield_refuses_to_invent_clock(self):
        elements,event,cfg=self.fixture(); event['source_summary']['photons']=5.
        with patch('lighthit.experimental.g4_source.load_event',return_value=elements),self.assertRaises(AssertionError):
            restored_axis_timing(event,cfg)


if __name__=='__main__':unittest.main()
