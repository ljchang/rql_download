#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013-2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""cubicweb-medicalexp container configuration"""

from cubes.container import ContainerConfiguration


CWSEARCH_RSET_CONTAINER = ContainerConfiguration("CWSearch", "rset")
CWSEARCH_RESULT_CONTAINER = ContainerConfiguration("CWSearch", "result")