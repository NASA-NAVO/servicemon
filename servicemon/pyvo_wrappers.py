import requests
import time
from time import sleep
from distutils.version import LooseVersion
from functools import partial

from codetiming import Timer
from astropy.io.votable import parse as votableparse

from pyvo.dal.tap import AsyncTAPJob, TAPService, TAPQuery, TAPResults
from pyvo.dal.exceptions import DALQueryError, DALServiceError
from pyvo.utils.http import use_session
from pyvo.io import uws

from .timing_labels import (TAP_SUBMIT, TAP_RUN, TAP_WAIT, TAP_RAISE_IF_ERROR,
                            TAP_FETCH_RESPONSE, TAP_DELETE)


class TAPServiceSM(TAPService):
    """
    Specialization of TAPService to support timing.
    """

    def run_sync_timed(
            self, query, language="ADQL", maxrec=None, uploads=None,
            streamable_response=False,
            **keywords):
        """
        runs sync query and returns its result

        Parameters
        ----------
        query : str
            The query
        language : str
            specifies the query language, default ADQL.
            useful for services which allow to use the backend query language.
        maxrec : int
            the maximum records to return. defaults to the service default
        uploads : dict
            a mapping from table names to objects containing a votable
        streamable_response: bool
            If False (default) return TapResult, otherwise return
            a streamable response.

        Returns
        -------
        TAPResults
            the query result

        See Also
        --------
        TAPResults
        """
        tap_query = self.create_query(
            query, language=language, maxrec=maxrec, uploads=uploads,
            **keywords)

        if streamable_response:
            # This block adapted from DALQuery.execute_stream()
            # to get a response instead of a response.raw.

            result = tap_query.submit()

            # Not clear if we want to catch this for the servicemon use case.
            try:
                result.raise_for_status()
            except requests.RequestException as ex:
                raise DALServiceError.from_except(ex)

        else:
            result = tap_query.execute()

        return result

    def run_async_timed(
            self, query, language="ADQL", maxrec=None, uploads=None,
            streamable_response=False, delete=False, **keywords):
        """
        runs async query and returns its result
         Parameters
        ----------
        query : str, dict
            the query string / parameters
        language : str
            specifies the query language, default ADQL.
            useful for services which allow to use the backend query language.
        maxrec : int
            the maximum records to return. defaults to the service default
        uploads : dict
            a mapping from table names to objects containing a votable
        streamable_response: bool
            If False (default) return TapResult, otherwise return
            a streamable response.
         Returns
        -------
        TAPResult or requests.packages.urllib3.response.HTTPResponse
            the query instance
         Raises
        ------
        DALServiceError
           for errors connecting to or communicating with the service
        DALQueryError
           for errors either in the input query syntax or
           other user errors detected by the service
        DALFormatError
           for errors parsing the VOTable response
         See Also
        --------
        AsyncTAPJob
        """
        with Timer(TAP_SUBMIT, logger=None):
            job = AsyncTAPSM.create(
                self.baseurl, query, language, maxrec, uploads, self._session, **keywords)

        with Timer(TAP_RUN, logger=None):
            job = job.run()

        with Timer(TAP_WAIT, logger=None):
            job = job.wait()

        with Timer(TAP_RAISE_IF_ERROR, logger=None):
            if job._job.phase in {"ERROR", "ABORTED"}:
                raise DALQueryError("Query Error", job._job.phase, job.url)

        with Timer(TAP_FETCH_RESPONSE, logger=None):
            if streamable_response:
                result = job.get_result_response()
            else:
                result = job.fetch_result()

        if delete:
            with Timer(TAP_DELETE, logger=None):
                job.delete()

        return result


class AsyncTAPSM(AsyncTAPJob):
    """
    Specialization of pyvo AsyncTAPJob to support timing.
    """

    _job = {}

    @classmethod
    def create(
            cls, baseurl, query, language="ADQL", maxrec=None, uploads=None,
            session=None, **keywords):
        """
        creates a async tap job on the server under `baseurl`
        Parameters
        ----------
        baseurl : str
            the TAP baseurl
        query : str
            the query string
        language : str
            specifies the query language, default ADQL.
            useful for services which allow to use the backend query language.
        maxrec : int
            the maximum records to return. defaults to the service default
        uploads : dict
            a mapping from table names to objects containing a votable
        session : object
           optional session to use for network requests
        """
        query = TAPQuery(
            baseurl, query, mode="async", language=language, maxrec=maxrec,
            uploads=uploads, session=session, **keywords)
        response = query.submit()
        uws_job = uws.parse_job(response.raw.read)
        job = cls(response.url, uws_job=uws_job, session=session)
        return job

    def __init__(self, url, uws_job=None, session=None):
        """
        initialize the job object with the given url and fetch remote values
        Parameters
        ----------
        url : str
            the job url
        """
        self._url = url
        self._session = use_session(session)

        self._job = uws_job

    def _update(self, wait_for_statechange=False, timeout=10.):
        """
        updates local job infos with remote values
        """
        try:
            if wait_for_statechange:
                response = self._session.get(
                    self.url, stream=True, timeout=timeout+5, params={
                        "WAIT": str(timeout)
                    }
                )
            else:
                response = self._session.get(self.url, stream=True, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as ex:
            raise DALServiceError.from_except(ex, self.url)

        # requests doesn't decode the content by default
        response.raw.read = partial(response.raw.read, decode_content=True)

        self._job = uws.parse_job(response.raw.read)

    def wait(self, phases=None, async_request_timeout=30,
             async_total_timeout=120):
        """
        waits for the job to reach the given phases.
        Parameters
        ----------
        phases : list
            phases to wait for
        Raises
        ------
        DALServiceError
            if the job is in a state that won't lead to an result
        """
        if not phases:
            phases = {"COMPLETED", "ABORTED", "ERROR"}

        interval = 1.0
        increment = 1.2

        active_phases = {
            "QUEUED", "EXECUTING", "RUN", "COMPLETED", "ERROR", "UNKNOWN"}

        supports_wait_for_statechange = (LooseVersion(self._job.version) >=
                                         LooseVersion("1.1"))
        if supports_wait_for_statechange:
            timeout = async_total_timeout
        else:
            timeout = async_request_timeout
        start_time = time.time()
        while True:
            self._update(wait_for_statechange=supports_wait_for_statechange,
                         timeout=timeout)

            elapsed = time.time() - start_time

            # use the cached value
            cur_phase = self._job.phase

            if cur_phase not in active_phases:
                raise DALServiceError(
                    "Cannot wait for job completion. Job is not active!")

            if cur_phase in phases:
                break

            # Check if we've exceeded total_timeout
            if elapsed > async_total_timeout:
                raise DALServiceError(
                    f'Async TAP job timed out, exceeding {async_total_timeout}s.')

            # fallback for uws 1.0
            if not supports_wait_for_statechange:
                sleep(interval)
                interval = min(120, interval * increment)

        return self

    def fetch_result(self):
        """
        returns the result votable if query is finished
        """
        response = self.get_result_response()

        response.raw.read = partial(
            response.raw.read, decode_content=True)
        return TAPResults(votableparse(response.raw.read), url=self.result_uri, session=self._session)

    def get_result_response(self):
        try:
            response = self._session.get(self.result_uri, stream=True)
            response.raise_for_status()
        except requests.RequestException as ex:
            # Got rid of an _update() that was here because it does yet another query.
            # It was probably there to ensure that _phase is set, but that's hopeless if we're
            # getting errors here.

            # We can add specialized error handling here if needed.
            self.raise_if_error()
            raise DALServiceError.from_except(ex, self.url)

        return response
