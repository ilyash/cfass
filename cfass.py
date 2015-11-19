#!/usr/bin/env python

# Somewhat more friendly CloudFormation syntax based on YAML.

# ==================== WARNING ====================
# TESTED MINIMALLY (one big real life JSON import+export+compare)
# USE WITH GREAT CARE
# ... and write tests if you have the time :)
# I ADVISE COMPARING OUTPUT JSON WITH PREVIOUS VERSIONS OF THE JSON BEFORE RUNNING.

# ==================== LICENSE ====================
# Copyright (c) 2015 Ilya Sher
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE

# ==================== What it does? ====================
# It converts your CloudFormation YAML-based syntax to JSON. It keeps same
# data structure except for the following transformations:

# Conversion 1:
# [IN]
# AWS::Type::Name ResourceName:
#   k1: v1
#   k2: v2
# [OUT]
# "ResourceName": {
#   "Type": "AWS::Type::Name",
#   "Properties": {"k1": "v1", "k2": "v2"}
#  }

# Conversion 2:
# [IN]
# Tags:
#   k1: v1
#   k2: v2
# [OUT]
# "Tags": [{"Key": "k1", "Value": "v1"}, {"Key": "k2", "Value": "v2"}]

# ==================== Code ====================

import argparse
import json
import yaml
import sys


def import_transform(data, path=None):
    """ Converts CloudFormation data structure to CFASS data structure """
    path = path or []
    if path and path[-1] == 'Tags':
        ret = {}
        for tag in data:
            ret[tag['Key']] = tag['Value']
        return ret
    if isinstance(data, dict):
        ret = {}
        for k, v in data.iteritems():
            if path and path[-1] == 'Resources':
                k = v['Type'] + ' ' + k
                ret[k] = import_transform(v['Properties'], path + [k, 'Properties'])
            else:
                ret[k] = import_transform(v, path + [k])
        return ret
    if isinstance(data, list):
        ret = []
        for idx, item in enumerate(data):
            ret.append(import_transform(item, path + [idx]))
        return ret
    return data


def export_transform(data, path=None):
    """ Converts CFASS data structure to CloudFormation data structure """
    path = path or []
    if path and path[-1] == 'Tags':
        ret = []
        for k, v in data.iteritems():
            ret.append({'Key': k, 'Value': v})
        return sorted(ret, key=lambda x: x['Key'])
    if isinstance(data, dict):
        ret = {}
        for k, v in data.iteritems():
            if path and path[-1] == 'Resources':
                res_type, res_name = k.split(' ')
                ret[res_name] = {'Type': res_type, 'Properties': export_transform(v, path + ['%RESOURCE%'])}
            else:
                ret[k] = export_transform(v, path + [k])
        return ret
    if isinstance(data, list):
        ret = []
        for idx, item in enumerate(data):
            ret.append(export_transform(item, path + [idx]))
        return ret
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CloudFormation Alernative Super Syntax. ' +
        'Translates syntax based on YAML (CFASS YAML) to CloudFormation JSON. ' +
        'Reads from standard input, writes to standard output. ' +
        'See "What it does?" section in cfass.py file for additional syntax enhancements. ' +
        'You can also import using --import flag an existing JSON to see an example and/or ' +
        'start using CFASS syntax immediately. ' +
        'See the MIT license inside cfass.py')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import: convert existing CloudFormation JSON to CFASS YAML format')
    parser.set_defaults(do_import=False)
    args = parser.parse_args()

    if args.do_import:
        data = import_transform(json.load(sys.stdin))
        yaml.safe_dump(data, stream=sys.stdout)
    else:
        data = export_transform(yaml.load(stream=sys.stdin))
        json.dump(data, sys.stdout)
