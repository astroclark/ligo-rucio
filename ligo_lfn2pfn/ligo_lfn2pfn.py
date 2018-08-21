"""
Default LFN-to-path algorithms for LIGO
"""
import re

from rucio.rse.protocols.protocol import RSEDeterministicTranslation

_GWF_RE = re.compile(r'([A-Z]+)-([A-Za-z0-9_]+)-([0-9]{5,5})(.*)')
_DATASET_RE = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)_([A-Za-z0-9_]+)')
def ligo_lab(scope, name, rse, rse_attrs, proto_attrs):
    """
    Map the GWF files according to the Caltech schema.

    ER8:H-H1_HOFT_C02-1126256640-4096 -> ER8/hoft_C02/H1/H-H1_HOFT_C02-11262/H-H1_HOFT_C02-1126256640-4096
    """
    # Prevents unused argument warnings in pylint
    del rse
    del rse_attrs
    del proto_attrs

    m = _GWF_RE.match(name)
    if not m:
        raise ValueError("Invalid LIGO filename")
    detector, dataset, gps_prefix, _ = m.groups()
    dir_hash = "%s-%s-%s" % (detector, dataset, gps_prefix)

    if detector == 'V':
        detector_pretty = 'AdVirgo'
        if dataset == 'V1Online':
            dataset = 'HrecOnline'
        return '%s/%s/%s/%s' % (scope, dataset, dir_hash, name)
    else:
        detector_pretty = detector[0] + '1'

    m = _DATASET_RE.match(dataset)
    if m:
        _, kind, calib = m.groups()
        if calib == 'C00':
            dataset_pretty = kind.lower()
        else:
            dataset_pretty = '%s_%s' % (kind.lower(), calib)
    else:
        dataset_pretty = dataset

    return "%s/%s/%s/%s/%s" % (scope, dataset_pretty, detector_pretty, dir_hash, name)


RSEDeterministicTranslation.register(ligo_lab)


if __name__ == '__main__':

    def test_cit_mapping(scope, name, pfn):
        mapped_pfn = ligo_lab(scope, name, None, None, None)
        if mapped_pfn == pfn:
            print "%s:%s -> %s" % (scope, name, pfn)
        else:
            print "FAILURE: %s:%s -> %s (expected %s)" % (scope, name, mapped_pfn, pfn)

    test_cit_mapping("postO1", "H-H1_HOFT_C00-1163149312-4096.gwf", "postO1/hoft/H1/H-H1_HOFT_C00-11631/H-H1_HOFT_C00-1163149312-4096.gwf")
    test_cit_mapping("postO1", "L-L1_HOFT_C00-1158533120-4096.gwf", "postO1/hoft/L1/L-L1_HOFT_C00-11585/L-L1_HOFT_C00-1158533120-4096.gwf")
    test_cit_mapping("O2", "H-H1_HOFT_C01-1188003840-4096.gwf", "O2/hoft_C01/H1/H-H1_HOFT_C01-11880/H-H1_HOFT_C01-1188003840-4096.gwf")
    test_cit_mapping("O1", "L-L1_HOFT_C01_4kHz-1137250304-4096.gwf", "O1/hoft_C01_4kHz/L1/L-L1_HOFT_C01_4kHz-11372/L-L1_HOFT_C01_4kHz-1137250304-4096.gwf")
    test_cit_mapping("AdVirgo", "V-V1Online-1192294000-2000.gwf", "AdVirgo/HrecOnline/V-V1Online-11922/V-V1Online-1192294000-2000.gwf")
    test_cit_mapping("O2", "V-V1O2Repro1A-1187990000-5000.gwf", "O2/V1O2Repro1A/V-V1O2Repro1A-11879/V-V1O2Repro1A-1187990000-5000.gwf")
