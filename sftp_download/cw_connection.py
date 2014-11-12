#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import sys
import urllib2
import urllib
import json
import csv
import logging
import time

# Define logger
logger = logging.getLogger(__name__)


def load_csv(csv_stream, delimiter=";"):
    """ Load a csv file.

    Parameters
    ----------
    csv_stream: open file (mandatory)
        the file stream we want to load.

    Returns
    -------
    csv_lines: list
        a list containing all the csv lines.
    """
    reader = csv.reader(csv_stream, delimiter=delimiter)
    csv_lines = [line for line in reader]

    return csv_lines


class CWInstanceConnection(object):
    """ Tool to dump the data stored in a cw instance.

    Attributes
    ----------
    url : str
        the url to the cw instance.
    login : str
        the cw login.
    opener:  OpenerDirector
        object that contains the connexion to the cw instance.
    """
    # Global variable that specify the supported export cw formats
    _EXPORT_TYPES = ["json", "csv", "fuse"]
    importers = {
        "json": json.load,
        "csv": load_csv,
        "fuse": json.load,
    }

    def __init__(self, url, login, password, realm=None):
        """ Initilize the HTTPConnection class.

        Parameters
        ----------
        url: str (mandatory)
            the url to the cw instance.
        login: str (mandatory)
            the cw login.
        password: str (mandatory)
            the cw user password.
        realm: str (optional default None)
            authentification domain (see firefox -> Outils -> Developpement web
            -> Reseau -> Get)
        """
        # Class parameters
        self.url = url
        self.login = login
        self.realm = realm
        self._connect(password)

    ###########################################################################
    # Public Members
    ###########################################################################

    def execute(self, rql, export_type="json"):
        """ Method that loads the rset from a rql request.

        Parameters
        ----------
        rql: str (mandatory)
            the rql rquest that will be executed on the cw instance.
        export_type: str (optional default 'json')
            the result set export format: one defined in '_EXPORT_TYPES'.

        Returns
        -------
        rset: list of list of str
            a list that contains the requested entity parameters.        
        """
        # Debug message
        logger.debug("Executing rql: '%s'", rql)
        logger.debug("Exporting in: '%s'", export_type)

        # Check export type
        if export_type not in self._EXPORT_TYPES:
            raise Exception("Unknown export type '{0}', expect one in "
                            "'{1}'.".format(export_type, self._EXPORT_TYPES))

        # Create a dictionary with the request meta information
        data = {
            "rql": rql,
            "vid": export_type + "export",
        }
        if export_type == "fuse":
            data.pop("rql")

        # Get the result set
        rset = self.importers[export_type](
            self.opener.open(self.url, urllib.urlencode(data)))

        # Debug message
        logger.debug("RQL result: '%s'", rset)

        return rset

    def execute_with_fuse(self, rql, sync_dir, timer=3, nb_of_try=3):
        """ Method that loads the rset from a rql request through the sftp
        fuse CWSearch mount point.

        Parameters
        ----------
        rql: str (mandatory)
            the rql rquest that will be executed on the cw instance.
        sync_dir: str (mandatory)
            the destination folder where the rql data are synchronized.
        timer: int (optional default 3)
            the time in seconds we are waiting for the fuse update.
        nb_of_try: int (optional default 3)
            if the fuse update has not been detected after 'nb_of_try' trials
            raise an exception.

        Returns
        -------
        rset: list of list of str
            a list that contains the requested entity parameters.        
        """
        # Create the CWSearch
        connection._create_cwsearch(rql)

        # Wait for fuse update: use double quote in rql
        try_nb = 1
        cwsearch_title = None
        rql = rql.replace("'", '"')
        while try_nb <= nb_of_try:

            # Timer
            logger.debug("Sleeping: '%i sec'", timer)
            time.sleep(timer)

            # Get all the user CWSearch in the database
            rset = self.execute(
                "Any S, T, P Where S is CWSearch, S title T, S path P")

            # Check if the fuse update has been done.
            # If true, get the associated CWSearch title
            for item in rset:
                if item[2].replace("'", '"') == rql:
                    cwsearch_title = item[1]
                    break
            if cwsearch_title is not None:
                break

            # Increment
            try_nb += 1

        # Rsync with the sftp fuse mount point
        print cwsearch_title
        self._rsync_fuse(sync_dir, cwsearch_title)

    ###########################################################################
    # Private Members
    ###########################################################################

    def _rsync_fuse(self, sync_dir, cwsearch_title):
        """
        """
        # Get instance parameters
        cw_params = self.execute(rql="", export_type="fuse")

    def _create_cwsearch(self, rql, export_type="cwsearch"):
        """ Method that creates a CWSearch entity from a rql.

        .. note::
        
            The CWSearch title has to be unique, build automatically title
            of the form 'auto_generated_title_x' where x is incremented
            each time an element is inserted in the data base.

        Parameters
        ----------
        rql: str (mandatory)
            the rql rquest that will be executed on the cw instance.
        """
        # Debug message
        logger.debug("Executing rql: '%s'", rql)
        logger.debug("Exporting in: '%s'", export_type)

        # Create a dictionary with the request meta information
        auto_generated_title = "auto_generated_title_1"
        data = {
            "path": rql,
            "title": auto_generated_title,
            "vid": export_type + "export",
        }

        # Get the result set
        response = self.opener.open(self.url, urllib.urlencode(data))

    def _connect(self, password):
        """ Method to create an object that handle opening of HTTP URLs.

        .. notes::

            If the Python installation has SSL support
            (i.e., if the ssl module can be imported),
            HTTPSHandler will also be added?

        Parameters
        ----------
        password: str (mandatory)
            the cw user password.       
        """
        # Create the handlers and the associated opener
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        if self.realm is not None:
            auth_handler = urllib2.HTTPBasicAuthHandler()
            auth_handler.add_password(realm=self.realm,
                                      uri=url,
                                      user=self.login,
                                      passwd=password)
            self.opener.add_handler(auth_handler)

        # Connect to the cw instance
        data = {
            "__login": self.login,
            "__password": password,
        }
        self.opener.open(self.url, urllib.urlencode(data))


if __name__ == "__main__":

    # Set logging level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    # Create dummy rql
    rql1 = ("Any C, G Where X is Subject, X code_in_study C, "
           "X handedness 'ambidextrous', X gender G")
    #rql1 = "Any C Where X is Subject, X code_in_study C"
    rql2 = ("Any S WHERE S is Scan, S r_concerns A, A code_in_study "
            "'000000022453'")
    #rql2 = ("Any S WHERE S is Scan, S has_data A, A field '3T', "
    #        "S in_assessment B, B timepoint 'V1', S format 'GIS', "
    #        "S in_assessment C, C concerns D, D code_in_study 'ab100207'")

    # HTTP test
    url = "http://mart.intra.cea.fr/imagen"; login = "admin"; password = "alpine"
    #url = "http://is223527.intra.cea.fr:8080"; login = "admin"; password = "a"
    connection = CWInstanceConnection(url, login, password)
    connection.execute(rql1, export_type="json")
    connection.execute_with_fuse(rql2, "/tmp/fuse", timer=1)

    # HTTPS test
    #url = "https://imagen2.cea.fr/database/"; login = "grigis"; password = "password"
    #connection = CWInstanceConnection(url, login, password, realm="Imagen")
    #connection.execute(rql)
