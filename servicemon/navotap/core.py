# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
=============
TAP plus
=============

"""
from astroquery.utils.tap.core import TapPlus


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
        args = {
            "PHASE": "RUN"}
        data = self._Tap__connHandler.url_encode(args)
        response = self._Tap__connHandler.execute_post('async/'+jobid+'/phase',
                                                       data)
        if verbose:
            print(response.status, response.reason)
            print(response.getheaders())
        return response
