import re
import itertools

import bokeh.plotting as plotting
from bokeh.models import Legend, ColumnDataSource, HoverTool, Div
import bokeh.transform as transform
import bokeh.layouts as layouts
from bokeh.palettes import Spectral6, Spectral11

import pandas as pd


def create_data_frame(data):
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
    `~pandas.core.frame.DataFrame`
        A Pandas data frame suitable for plotting most quantities.
    """
    # Masked values in integer columns show up as <NA> when exported to Pandas.
    # Such values seem to cause weird errors when displayed in bokeh, even when those rows
    # are filtered out with dropna().  So convert the column to float, which results
    # in masked values being NaN (np.nan) which are smoothly ignored by bokeh.
    data["num_rows"] = data["num_rows"].astype(float)
    data["size"] = data["size"].astype(float)

    # This one gives us one value for the whole day which is something we can group on.
    data['datestr'] = data['start_time'].astype('U10')

    # Create the Pandas DataFrame, with start time officially being a datetime.
    df = data["location", "start_time", "datestr", "do_query_dur", "query_total_dur", "stream_to_file_dur",
              "size", "num_rows", "base_name", "service_type", "ra", "dec", "sr"].to_pandas().copy()
    df["dt_start_time"] = pd.to_datetime(df["start_time"], format='%Y-%m-%d %H:%M:%S.%f')

    # A datetime version of the date rounded to a whole day.
    df["date"] = pd.to_datetime(df["datestr"], format='%Y-%m-%d')

    # Data volume (bytes per query second)
    df['rate'] = df['size'] / df['query_total_dur']

    return df


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
            ("Download Size", "@size"),
            ("# of Rows", "@num_rows"),
            ("Location", "@location"),
            ("Start Time", "@dt_start_time{%m/%d %H:%M:%S}")
        ],
        formatters={
            '@dt_start_time': 'datetime'
        })
    return hover


def get_locations(df):
    """
    Get the list of all locations present in the data source.

    Parameters
    ----------
    df : `~pandas.core.frame.DataFrame`
        Astropy data table containing the navostats data

    Returns
    -------
    list of str
        Sorted unique location values present in the data.
    """
    dfg = df.groupby(['location'])
    locations = list(dfg.groups)
    locations.sort()
    return locations


def create_plot_dur_v_start_time(source, locations, y_axis_type='log', y_range=(0.001, 10**3)):
    """
    Create a Bokeh plot (Figure) of do_query_dur versus start_time.

    Parameters
    ----------
    source : ColumnDataSource
        Bokeh data source containing the navostats data
    locations : list of str
        List of unique location values in the data source.
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

    index_cmap = transform.factor_cmap('location', palette=Spectral6, factors=locations, end=1)

    # add renderers
    p.circle(x="dt_start_time", y="do_query_dur", source=source, size=4, color=index_cmap, alpha=0.5,
             legend_group="location")

    p.title.text = "Query Duration v. Start Time"
    p.xaxis.axis_label = 'Start Time'
    p.yaxis.axis_label = 'Duration (s)'
    p.legend.location = (0, 0)
    p.add_layout(p.legend[0], 'below')

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


def create_plot_durations_v_size(source, x_axis_type='log', x_range=(100, 10**9),
                                 y_axis_type='log', y_range=(0.0001, 10**3)):
    """
    Create a Bokeh plot (Figure) of do_query_dur and stream_to_file_dur versus download size.
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
    qt_rend = p.circle(x="size", y="do_query_dur", source=source, size=4, color='red', alpha=0.2)
    dt_rend = p.circle(x="size", y="stream_to_file_dur", source=source, size=4, color='green', alpha=0.2)

    legend = Legend(items=[
        ("Query Duration",   [qt_rend]),
        ("Download Duration", [dt_rend])
    ], location=(0, 0), click_policy='hide')
    p.add_layout(legend, 'below')

    p.title.text = 'Query and Download Durations v. Download Size'
    p.xaxis.axis_label = 'Response size (bytes)'
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

    layout_children, _ = generate_service_plots(stat_queries, services, start_time, end_time)
    bk_layout = layouts.layout(children=layout_children)

    if htmlfile is None:
        plotting.output_notebook()
        plotting.show(bk_layout)
    else:
        plotting.output_file(htmlfile, title=title)
        plotting.save(bk_layout)


def generate_summary_plots(stat_queries, services, start_time, end_time):
    """

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
    list of lists, list of dicts
        list of layout children rows, each of which is a list of plots or divs
        and list of "id" and "title" dicts for populating a TOC
    """

    # Build the layout.
    layout_children = []
    rows_toc = []

    data = stat_queries.do_stat_query(start_time=start_time, end_time=end_time)
    df = create_data_frame(data)

    # Make one group df per service/service_type pair.
    date_groups = []
    for s in services:
        service_df = df[df['base_name'] == s[0]]
        service_and_type_df = service_df[service_df['service_type'] == s[1]]
        g = service_and_type_df.groupby('date')
        date_groups.append(g)

    # Build naming and ToC.
    row_title = f'Summary Plots from {start_time[:10]} to {end_time[:10]}'
    row_label = {
        "id": re.sub('\\s+', '_', row_title),
        "title": row_title
    }
    rows_toc.append(row_label)

    daily_duration_line_plot = create_daily_duration_line_plot(date_groups, services)
    daily_rate_line_plot = create_daily_rate_line_plot(date_groups, services)

    layout_children.append([Div(text='<hr><h1 style="min-width:800px" id="{id}">{title}</h1>'.format(**row_label))])
    layout_children.append([daily_duration_line_plot, daily_rate_line_plot])

    return layout_children, rows_toc


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
    list of lists, list of dicts
        list of layout children rows, each of which is a list of plots or divs
        and list of "id" and "title" dicts for populating a TOC
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
        df = create_data_frame(data)
        source = ColumnDataSource(df)

        locations = get_locations(df)
        over_time_plot = create_plot_dur_v_start_time(source, locations)
        time_v_nrows_plot = create_plot_durations_v_size(source)

        layout_children.append([Div(text='<hr><h1 style="min-width:800px" id="{id}">{title}</h1>'.format(**row_label))])
        layout_children.append([over_time_plot, time_v_nrows_plot])

    return layout_children, rows_toc


def create_daily_rate_line_plot(sources, services, y_axis_type='log', y_range=(1, 10**7)):
    """


    Returns
    -------
    plotting.figure
        A Bokeh plot that can be shown.
    """

    # create plot with a datetime axis type
    p = plotting.figure(plot_width=700, plot_height=1200, x_axis_type="datetime",
                        y_axis_type=y_axis_type, y_range=y_range)

    line_dashes = ['solid'] * 11
    line_dashes.extend(['dashed'] * 11)
    line_dashes.extend(['dotted'] * 11)
    for source, service, color, line_dash in zip(sources, services,
                                                 itertools.cycle(Spectral11), line_dashes):
        legend_label = f'{service[0]} {service[1]}'
        p.line(x='date', y='rate_mean', line_width=2, source=source, color=color,
               legend_label=legend_label, line_dash=line_dash)

    p.legend.click_policy = "hide"

    p.title.text = "Mean Daily Bytes per Second v. Start Time"
    p.xaxis.axis_label = 'Start Time'
    p.yaxis.axis_label = 'Mean Bytes per Second (s)'

    p.legend.location = (0, 0)
    p.add_layout(p.legend[0], 'below')

    return p


def create_daily_duration_line_plot(sources, services, y_axis_type='log', y_range=(0.1, 1000)):
    """
    Returns
    -------
    plotting.figure
        A Bokeh plot that can be shown.
    """

    # create plot with a datetime axis type
    p = plotting.figure(plot_width=700, plot_height=1200, x_axis_type="datetime",
                        y_axis_type=y_axis_type, y_range=y_range)

    line_dashes = ['solid'] * 11
    line_dashes.extend(['dashed'] * 11)
    line_dashes.extend(['dotted'] * 11)
    for source, service, color, line_dash in zip(sources, services,
                                                 itertools.cycle(Spectral11), line_dashes):
        legend_label = f'{service[0]} {service[1]}'
        p.line(x='date', y='query_total_dur_mean', line_width=2, source=source, color=color,
               legend_label=legend_label, line_dash=line_dash)

    p.legend.click_policy = "hide"

    p.title.text = "Mean Daily Query Duration v. Start Time"
    p.xaxis.axis_label = 'Start Time'
    p.yaxis.axis_label = 'Mean Query Duration (s)'

    p.legend.location = (0, 0)
    p.add_layout(p.legend[0], 'below')

    return p


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
