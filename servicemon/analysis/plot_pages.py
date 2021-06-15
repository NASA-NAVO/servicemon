import os
from datetime import datetime, timedelta
from bokeh.embed import components
import bokeh.layouts as layouts
import jinja2
from argparse import ArgumentParser

from .basic_plotting import generate_service_plots, generate_summary_plots
from .stat_queries import StatQueries


def sm_create_weekly_plots(input_args=None):
    parser = ArgumentParser(description='Create HTML page with weekly plots')

    parser.add_argument(
        'date_to_include',
        help="""Date (YYYY-MM-DD) defining the week for which to make plots.
If specified, the plot week will start at 00:00 on the most recent Monday including the date.
If not specified, the plot week will be the most recent full week starting on a Monday.""",
        nargs='?', default=None)

    args = parser.parse_args(input_args)
    create_weekly_plots(args.date_to_include)


def create_weekly_plots(date_to_include=None):
    """
    Helper function to create an HTML page containing bokeh plots
    for one week's worth of servicemon data for all the services in the TAP DB.
    The week of data starts on Monday and includes ``date_to_include``.

    The created file will be stored in the directory ``htmlroot/stat_pages`` and
    will be called ``YYYY-MM-DD.html`` where YYYY-MM-DD indicate the Monday at the
    start of the week.

    Parameters
    ----------
    date_to_include : str default=None
        Date of the form YYYY-MM-DD to include in the week's worth of stats.
        If None, the most recent full Monday through Sunday week will be used.

    Returns
    -------
    None
    """
    start_time = _compute_start_of_week(date_to_include)

    # Get all the available name/service pairs.
    sq = StatQueries()
    services = sq.get_name_service_pairs()

    create_service_plots_page(sq, services, start_time, delta=timedelta(days=7))


def create_service_plots_page(stat_queries, services, start_time,
                              end_time=None, delta=None, htmlroot='htmlroot'):
    """
    Create an HTML page containing bokeh plots for a time interval's worth of
    servicemon data for each of the service name/type pairs (``services``).

    The created file will be stored in the directory ``[htmlroot]/stat_pages`` and
    will be called ``YYYY-MM-DD.html`` where YYYY-MM-DD is the ``start_time``.

    Parameters
    ----------
    stat_queries : servicemon.analysis.stat_queriesStatQueries
        A StatQueries object which will perform the navostats queries.
    services : List of tuples
        Each tuple should be a doubleton indicating a (base_name, service_type)
        that should be queried and plotted.
    start_time : str
        The beginning of a time window bounding the query.  Format is '%Y-%m-%d %H:%M:%S.%f'.
        Least significant part can be omitted as the comparisons done are just alphabetic.
    end_time : str default=None
        The end of a time window bounding the query.  Format is '%Y-%m-%d %H:%M:%S.%f'.
        Least significant part can be omitted as the comparisons done are just alphabetic.

        If None, then ``delta`` will be used to determine the end of the time interval.
        If ``delta`` is also not present, then the interval extends to the present time.
        Both ``end_time`` and ``delta`` cannot be present in the same call.
    delta : timedelta default=None
        Specifies the duration of the time interval.  E.g., ``delta=timedelta(days=7)``
        gives an interval duration of 1 week.

        If None, then ``end_time`` will be used to determine the end of the time interval.
        If ``end_time`` is also not present, then the interval extends to the present time.
        Both ``end_time`` and ``delta`` cannot be present in the same call.
    htmlroot : str default='htmlroot'
        The directory in which to output the ``stat_pages/YYYY-MM-DD.html`` result file.

    Returns
    -------
    None
    """
    # Validate the input.
    if end_time is not None and delta is not None:
        raise ValueError('Only one of end_time and delta can be specified.')
    if delta is not None and not isinstance(delta, timedelta):
        raise ValueError('delta must be of type timedelta')
    start_dt = datetime.fromisoformat(start_time)

    # Compute the title, and end_time if necessary.
    if end_time is None:
        if delta is not None:
            title = f'Statistics from {start_time} for {delta}'
            end_dt = start_dt + delta
            end_time = datetime.strftime(end_dt, '%Y-%m-%d %H:%M:%S.%f')
    else:
        title = f'Statistics from {start_time} to {end_time}'

    # Make the output path.
    stat_page_path = f'{htmlroot}/stat_pages'
    os.makedirs(stat_page_path, exist_ok=True)
    htmlfile = f'{stat_page_path}/{start_time}.html'

    # Get the layout children and toc items for the service plots.
    min_time = '2021-04-05'
    _, summary_start_time = with_delta(end_time, delta=timedelta(days=-35))
    if summary_start_time < min_time:
        summary_start_time = min_time
    layout_children, rows_toc = generate_summary_plots(stat_queries, services, summary_start_time, end_time)

    # Get the layout children and toc items for the service plots.
    service_layout_children, service_rows_toc = generate_service_plots(stat_queries, services, start_time, end_time)

    layout_children.extend(service_layout_children)
    rows_toc.extend(service_rows_toc)

    # Build the layout.
    bk_layout = layouts.layout(children=layout_children)

    # Build the template and render the layout content.
    script, div = components(bk_layout)
    top_body = _build_top_body(title, rows_toc)
    jtemplate = _build_jinja_template(title, top_body)
    html = jtemplate.render(script=script, div=div)

    # Write out the file.
    with open(htmlfile, 'w') as f:
        f.write(html)


def with_delta(t, delta):
    """
    Return the datetime and time string for a time that is delta different than t.

    Parameters
    ----------
    t : str or datetime
        Base time as an iso time string or datetime object
    delta : timedelta
        Amount of time to add to t.  E.g., ``delta=timedelta(days=7)``


    Returns
    -------
    (datetime, str)
        The time resulting from t + delta as both datetime and str
    """
    if not isinstance(delta, timedelta):
        raise ValueError('delta must be a timedelta object.')

    # Ensure t_dt is a datetime
    t_dt = t
    if not isinstance(t, datetime):
        t_dt = datetime.fromisoformat(t)

    result_dt = t_dt + delta
    result_str = datetime.strftime(result_dt, '%Y-%m-%d %H:%M:%S.%f')

    return result_dt, result_str


def _compute_start_of_week(date_to_include=None):
    # Set include_dt to a datetime within the week of interest.
    if date_to_include is not None:
        # The given date_to_include defines the week of interest.
        include_dt = datetime.fromisoformat(date_to_include)
    else:
        # We will use a date from one week ago to ensure that the week of interest is a full week.
        include_dt = datetime.now() - timedelta(days=7)

    # The start_time for the query will be the beginning of the week of interest.
    year, week, _ = include_dt.isocalendar()
    start_dt = datetime.fromisocalendar(year, week, 1)
    start_time = datetime.strftime(start_dt, '%Y-%m-%d')
    return start_time


def _build_top_body(title, rows_toc):
    top_body = f'''
    <h1>{title}</h1>
    <div id="toc_container">
    <p class="toc_title">Plots</p>
    <ul class="toc_list">
    '''
    for row in rows_toc:
        new_row = '<li><a href="#{id}">{title}</a></li>\n'.format(**row)
        top_body += new_row

    top_body += '''
    </ul>
    </div>
    '''

    return top_body


def _build_jinja_template(title, top_body):
    # Add the title and scripts to load.
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
      <head>
          <meta charset="utf-8">
          <title>{title}</title>
          <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-2.3.1.min.js"
          integrity="sha384-YF85VygJKMVnHE+lLv2AM93Vbstr0yo2TbIu5v8se5Rq3UQAUmcuh4aaJwNlpKwa" crossorigin="anonymous">
          </script>
          <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.3.1.min.js"
          integrity="sha384-KKuas3gevv3PvrlkyCMzffFeaMq5we/a2QsP5AUoS3mJ0jmaCL7jirFJN3GoE/lM" crossorigin="anonymous">
          </script>
          <script type="text/javascript">
              Bokeh.set_log_level("info");
          </script>
    '''

    # Add the style for the Table of Contents
    html += '''
        <style>
        #toc_container {
            background: #f9f9f9 none repeat scroll 0 0;
            border: 1px solid #aaa;
            display: table;
            margin-bottom: 1em;
            padding: 20px;
            width: auto;
        }

        .toc_title {
            font-weight: 700;
            text-align: left;
            font-size: larger;
        }

        #toc_container li, #toc_container ul, #toc_container ul li{
            list-style: outside none none !important;
        }
        </style>

    </head>

    <body>
    '''

    # Add the provided top_body and placeholder for bokeh scripts and divs.
    html += top_body
    html += '''
        {{ script }}

        {{ div }}
    </body>
    </html>'''

    jtemplate = jinja2.Template(html)
    return jtemplate
