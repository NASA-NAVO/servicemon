# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
=============
TAP plus
=============

"""
import requests

from astroquery.utils.tap.core import TapPlus
from astroquery.utils.tap.model.job import Job


__all__ = ['TapPlusNavo']

VERSION = "1.0.1"
TAP_CLIENT_ID = "aqtappy-" + VERSION


class TapPlusNavo(TapPlus):
    """TAP plus class
    Provides TAP and TAP+ capabilities

    Notes
    -----------------
    To override some parts of the utils/tap library in order for it to
    work around the autostart issue.
    """

    def __init__(self, url=None, host=None, server_context=None,
                 tap_context=None, port=80, sslport=443,
                 default_protocol_is_https=False, connhandler=None,
                 agent=None, verbose=False):
        """

        Parameters
        ----------
        url : str, mandatory if no host is specified, default None
            TAP URL
        host : str, optional, default None
            host name
        server_context : str, optional, default None
            server context
        tap_context : str, optional, default None
            tap context
        port : int, optional, default '80'
            HTTP port
        sslport : int, optional, default '443'
            HTTPS port
        default_protocol_is_https : bool, optional, default False
            Specifies whether the default protocol to be used is HTTPS
        connhandler connection handler object, optional, default None
            HTTP(s) connection hander (creator). If no handler is provided, a
            new one is created.
        agent : User-Agent string, optional, default None
        verbose : bool, optional, default 'False'
            flag to display information about the process
        """

        super(TapPlusNavo, self).__init__(url, host, server_context,
                                          tap_context, port, sslport,
                                          default_protocol_is_https,
                                          connhandler, verbose)

        # Hack to set the User-Agent on TAP requests.
        if agent is not None:
            ch = self._Tap__connHandler
            self.set_header_agent(ch._TapConn__postHeaders, agent)
            self.set_header_agent(ch._TapConn__getHeaders, agent)

    def set_header_agent(self, header, agent):
        if header is not None:
            header.update({
                'User-Agent': agent
            })

    def _Tap__launchJob(self, query, outputFormat,
                        context, verbose, name=None):
        """

        Notes
        -----------------
        Get rid of PHASE:RUN in args and if async job send PHASE:RUN to
        async/phase in order to get the job to run
        """
        args = {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": str(outputFormat),
            "tapclient": str(TAP_CLIENT_ID),
            "QUERY": str(query)}
        data = self._Tap__connHandler.url_encode(args)
        response = self._Tap__connHandler.execute_post(context, data)
        if verbose:
            print(response.status, response.reason)
            print(response.getheaders())
        if 'async' in context:
            location = self._Tap__connHandler.find_header(
                response.getheaders(),
                "location")
            jobid = self._Tap__getJobId(location)
            runresponse = self.__runAsyncQuery(jobid, verbose)
            return runresponse
        return response

    def __runAsyncQuery(self, jobid, verbose):
        """
        Notes
        ------------------
        This was added in order to run the job after it was created
        """
        if verbose:
            print(f'Running async query for job: {jobid}')
        args = {
            "PHASE": "RUN"}
        data = self._Tap__connHandler.url_encode(args)
        response = self._Tap__connHandler.execute_post('async/'+jobid+'/phase',
                                                       data)
        if verbose:
            print(response.status, response.reason)
            print(response.getheaders())
        return response

    def launch_job(self, query, name=None, output_file=None,
                   output_format="votable", verbose=False,
                   dump_to_file=False, upload_resource=None,
                   upload_table_name=None):
        """Launches a synchronous job

        Parameters
        ----------
        query : str, mandatory
            query to be executed
        output_file : str, optional, default None
            file name where the results are saved if dumpToFile is True.
            If this parameter is not provided, the jobid is used instead
        output_format : str, optional, default 'votable'
            results format
        verbose : bool, optional, default 'False'
            flag to display information about the process
        dump_to_file : bool, optional, default 'False'
            if True, the results are saved in a file instead of using memory
        upload_resource: str, optional, default None
            resource to be uploaded to UPLOAD_SCHEMA
        upload_table_name: str, required if uploadResource is provided, default None
            resource temporary table name associated to the uploaded resource

        Returns
        -------
        A Job object
        """
        # Do not limit these queries. query = taputils.set_top_in_query(query, 2000)
        if verbose:
            print("Launched sync query: '"+str(query)+"'")
        if upload_resource is not None:
            if upload_table_name is None:
                raise ValueError("Table name is required when a resource is uploaded")
            response = self._Tap__launchJobMultipart(
                query, upload_resource, upload_table_name,
                output_format, "sync", verbose, name)
        else:
            response = self._Tap__launchJob(query,
                                            output_format,
                                            "sync",
                                            verbose,
                                            name)
        # handle redirection
        if response.status == 303:
            # redirection
            if verbose:
                print("Redirection found")
            location = self._Tap__connHandler.find_header(
                response.getheaders(),
                "location")
            if location is None:
                raise requests.exceptions.HTTPError("No location found after redirection was received (303)")
            if verbose:
                print("Redirect to %s", location)
            subcontext = self._Tap__extract_sync_subcontext(location)
            response = self._Tap__connHandler.execute_get(subcontext)
        job = Job(async_job=False, query=query, connhandler=self._Tap__connHandler)
        isError = self._Tap__connHandler.check_launch_response_status(
            response, verbose, 200)
        suitableOutputFile = self._Tap__getSuitableOutputFile(
            False, output_file, response.getheaders(), isError,
            output_format)
        job.outputFile = suitableOutputFile
        job.parameters['format'] = output_format
        job.set_response_status(response.status, response.reason)
        if isError:
            job.set_failed(True)
            if dump_to_file:
                self._Tap__connHandler.dump_to_file(suitableOutputFile, response)
            raise requests.exceptions.HTTPError(response.reason)
        else:
            pass
        return job, response
