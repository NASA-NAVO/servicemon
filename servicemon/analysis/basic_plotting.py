import re
import bokeh.plotting as plotting
from bokeh.models import Legend, ColumnDataSource, HoverTool, Div
import bokeh.transform as transform
import bokeh.layouts as layouts

import pandas as pd


def create_source(data):
    """
    Create a Bokeh ColumnDataSource from an Astropy Table containing results from
    a navostats query.


    Parameters
    ----------
    data : astropy.table.Table
        A table presumed to contain the results from a query on navostats.
        In particular, the following columns must be present: location, start_time,
        do_query_dur, stream_to_file_dur, num_rows, base_name, service_type, ra, dec, sr

    Returns
    -------
    ColumnDataSource
        A Bokeh data source suitable for plotting
    """
    # Masked values in integer columns show up as <NA> when exported to Pandas.
    # Such values seem to cause weird errors when displayed in bokeh, even when those rows
    # are filtered out with dropna().  So convert the column to float, which results
    # in masked values being NaN (np.nan) which are smoothly ignored by bokeh.
    data["num_rows"] = data["num_rows"].astype(float)

    # Create the Pandas DataFrame, with start time officially being a datetime.
    df = data["location", "start_time", "do_query_dur", "stream_to_file_dur", "num_rows", "base_name", "service_type",
              "ra", "dec", "sr"].to_pandas().copy()
    df["dt_start_time"] = pd.to_datetime(df["start_time"], format='%Y-%m-%d %H:%M:%S.%f')

    # Create the bokeh data source from the data frame.
    source = ColumnDataSource(df)

    return source


def create_hover():
    """
    Returns
    -------
    HoverTool
        A Bokeh hover tool which can provide a tooltip for plotted data points.
    """
    hover = HoverTool(
        tooltips=[
            ("Cone", "@ra, @dec, @sr"),
            ("Query Time", "@do_query_dur"),
            ("Download Time", "@stream_to_file_dur"),
            ("# of Rows", "@num_rows"),
            ("Location", "@location"),
            ("Start Time", "@dt_start_time{%m/%d %H:%M:%S}")
        ],
        formatters={
            '@dt_start_time': 'datetime'
        })
    return hover


def create_plot_dur_v_start_time(source, y_axis_type='log', y_range=(0.001, 10**3)):
    """
    Create a Bokeh plot (Figure) of do_query_dur versus start_time.

    Parameters
    ----------
    source : ColumnDataSource
        Bokeh data source containing the navostats data
    y_axis_type : str
        auto, linear, log, datetime, or mercator
    y_range : tuple (min, max)
        The range of values to display on the y axis.  When y_axis_type is 'log',
        it helps if the endpoints are exact powers of 10.

    Returns
    -------
    plotting.figure
        A Bokeh plot that can be shown.
    """

    # create plot with a datetime axis type
    p = plotting.figure(plot_width=700, plot_height=500, x_axis_type="datetime",
                        y_axis_type=y_axis_type, y_range=y_range)

    hover = create_hover()
    p.add_tools(hover)

    # add renderers
    p.circle(x="dt_start_time", y="do_query_dur", source=source, size=4, color='red', alpha=0.2)

    p.title.text = "Query Duration v. Start Time"
    p.xaxis.axis_label = 'Start Time'
    p.yaxis.axis_label = 'Duration (s)'

    return p


def create_plot_durations_v_nrows(source, x_axis_type='log', x_range=(1, 10**5),
                                  y_axis_type='log', y_range=(0.001, 10**3)):
    """
    Create a Bokeh plot (Figure) of do_query_dur and stream_to_file_dur versus num_rows.
    num_rows is the number of result rows from the query.

    Parameters
    ----------
    source : ColumnDataSource
        Bokeh data source containing the navostats data
    x_axis_type : str
        auto, linear, log, datetime, or mercator
    x_range : tuple (min, max)
        The range of values to display on the x axis.  When x_axis_type is 'log',
        it helps if the endpoints are exact powers of 10.
    y_axis_type : str
        auto, linear, log, datetime, or mercator
    y_range : tuple (min, max)
        The range of values to display on the y axis.  When y_axis_type is 'log',
        it helps if the endpoints are exact powers of 10.

    Returns
    -------
    plotting.figure
        A Bokeh plot that can be shown.
    """
    # create a new plot with a datetime axis type
    p = plotting.figure(plot_width=500, plot_height=500,
                        x_axis_type=x_axis_type, x_range=x_range,
                        y_axis_type=y_axis_type, y_range=y_range)

    hover = create_hover()
    p.add_tools(hover)

    # add renderers
    qt_rend = p.circle(x="num_rows", y="do_query_dur", source=source, size=4, color='red', alpha=0.2)
    dt_rend = p.circle(x="num_rows", y="stream_to_file_dur", source=source, size=4, color='green', alpha=0.2)

    legend = Legend(items=[
        ("Query Duration",   [qt_rend]),
        ("Download Duration", [dt_rend])
    ], location=(0, 40), click_policy='hide')
    p.add_layout(legend, 'below')

    p.title.text = 'Query and Download Durations v. # of Rows'
    p.xaxis.axis_label = '# of Rows'
    p.yaxis.axis_label = 'Durations (s)'

    return p


def create_service_plots(stat_queries, services, start_time=None, end_time=None, htmlfile=None, title=None):
    """    Create a Bokeh plot (Figure) of do_query_dur and stream_to_file_dur versus num_rows.
    num_rows is the number of result rows from the query.

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
    end_time : str
        The end of a time window bounding the query.  Format is '%Y-%m-%d %H:%M:%S.%f'.
        Least significant part can be omitted as the comparisons done are just alphabetic.
    htmlfile : str
        The name of the output html file.  Specify None if notebook output is desired.
    title : str
        The title given to the output html page.  Ignored if htmlfile is None.

    Returns
    -------
    None
    """
    plotting.reset_output()
    if htmlfile is None:
        plotting.output_notebook()
    else:
        plotting.output_file(htmlfile, title=title)

    bk_layout, _ = generate_service_plots(stat_queries, services, start_time, end_time)
    plotting.show(bk_layout)


def generate_service_plots(stat_queries, services, start_time, end_time):
    """    Create a Bokeh plot (Figure) of do_query_dur and stream_to_file_dur versus num_rows
    for each row, put the plot rows into a bokeh layout with title divs for each row, then
    return the layout.  Also return a list of dicst, one element per row, with "title" and "id"
    of the row.

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
    end_time : str
        The end of a time window bounding the query.  Format is '%Y-%m-%d %H:%M:%S.%f'.
        Least significant part can be omitted as the comparisons done are just alphabetic.

    Returns
    -------
    `~bokeh.layouts.layout`, List of dicts
    """

    # Build the layout.
    layout_children = []
    rows_toc = []

    for s in services:
        # Build naming and ToC.
        base_name = s[0]
        service_type = s[1]
        row_title = f'{base_name} {service_type}'
        row_label = {
            "id": re.sub('\\s+', '_', row_title),
            "title": row_title
        }
        rows_toc.append(row_label)

        data = stat_queries.do_stat_query(base_name=base_name, service_type=service_type,
                                          start_time=start_time, end_time=end_time)
        source = create_source(data)

        over_time_plot = create_plot_dur_v_start_time(source)
        time_v_nrows_plot = create_plot_durations_v_nrows(source)

        layout_children.append([Div(text='<hr><h1 style="min-width:800px" id="{id}">{title}</h1>'.format(**row_label))])
        layout_children.append([over_time_plot, time_v_nrows_plot])

    bk_layout = layouts.layout(children=layout_children)

    return bk_layout, rows_toc


def create_plot_location_shapes(source):
    """
    Experimental function to plot the different locations from which the performance queries
    were made as different shapes.
    """

    LOCATIONS = ['ap-northeast-1',
                 'ap-southeast-2',
                 'eu-west-3',
                 'sa-east-1',
                 'us-east-1',
                 'us-west-2'
                 ]

    MARKERS = ['asterisk',
               'circle',
               'diamond',
               'plus',
               'square',
               'triangle'
               ]

    p = plotting.figure(plot_width=500, plot_height=500,
                        x_axis_type='log', x_range=(0.001, 10**3),
                        y_axis_type='log', y_range=(1, 10**5))
    p.title.text = 'Duration v. # of Rows'
    p.xaxis.axis_label = 'Duration (s)'
    p.yaxis.axis_label = '# of Rows'

    p.scatter("do_query_dur", "num_rows", source=source,
              legend_field="location",
              fill_alpha=0.4, size=4,
              marker=transform.factor_mark('location', MARKERS, LOCATIONS),
              color='red',
              alpha=0.2)

    # Commenting this out for now.  Drawing the location shapes this way exposes a limitation
    # with Bokeh where clicking anywhere in the legend hides everything.
    # I think the locations would have to be drawn separately for the legend click hiding to
    # work as expected.
    # p.legend.click_policy="hide"

    p.legend.location = (0, 0)
    p.add_layout(p.legend[0], 'below')

    return p
