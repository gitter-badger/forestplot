import pandas as pd
from typing import Optional, List, Union, Tuple, Sequence, Any
import numpy as np

np.seterr(all="ignore")
import matplotlib.pyplot as plt
from matplotlib.pyplot import Axes
from forestplot.arg_validators import check_data
from forestplot.text_utils import form_est_ci
from forestplot.text_utils import normalize_varlabels
from forestplot.text_utils import indent_nongroupvar
from forestplot.text_utils import format_varlabels
from forestplot.text_utils import star_pval
from forestplot.text_utils import prep_annote
from forestplot.text_utils import prep_rightannnote
from forestplot.text_utils import make_tableheaders
from forestplot.dataframe_utils import insert_groups
from forestplot.dataframe_utils import sort_groups
from forestplot.dataframe_utils import sort_data
from forestplot.dataframe_utils import reverse_dataframe
from forestplot.graph_utils import right_flush_yticklabels
from forestplot.graph_utils import draw_pval_right
from forestplot.graph_utils import draw_ylabel1
from forestplot.graph_utils import format_xlabel
from forestplot.graph_utils import format_tableheader
from forestplot.graph_utils import draw_yticklabel2
from forestplot.graph_utils import remove_ticks
from forestplot.graph_utils import format_grouplabels
from forestplot.graph_utils import draw_ci
from forestplot.graph_utils import draw_est_markers
from forestplot.graph_utils import draw_ref_xline
from forestplot.graph_utils import despineplot
from forestplot.graph_utils import format_xticks
from forestplot.graph_utils import draw_alt_row_colors
from forestplot.graph_utils import draw_tablelines
from matplotlib import rcParams

rcParams["font.monospace"] = [
    "Lucida Sans Typewriter",
    "DejaVu Sans Mono",
    "Courier New",
    "Lucida Console",
]


def forestplot(
    dataframe: pd.core.frame.DataFrame,
    estimate: str,
    varlabel: str,
    moerror: Optional[str] = None,
    ll: Optional[str] = None,
    hl: Optional[str] = None,
    form_ci_report: bool = True,
    ci_report: bool = True,
    groupvar: Optional[str] = None,
    group_order: Optional[Union[list, tuple]] = None,
    annote: Optional[Union[Sequence[str], None]] = None,
    annoteheaders: Optional[Union[Sequence[str], None]] = None,
    rightannote: Optional[Union[Sequence[str], None]] = None,
    right_annoteheaders: Optional[Union[Sequence[str], None]] = None,
    pval: Optional[str] = None,
    starpval: bool = True,
    sort: bool = False,
    sortby: Optional[str] = None,
    flush: bool = True,
    decimal_precision: int = 2,
    figsize: Union[Tuple, List] = (4, 8),
    xticks: Optional[Union[list, range]] = None,
    ylabel: Optional[str] = None,
    xlabel: Optional[str] = None,
    yticker2: Optional[str] = None,
    color_alt_rows: bool = False,
    return_df: bool = False,
    preprocess: bool = True,
    table: bool = False,
    **kwargs: Any,
) -> Axes:
    """
    Draw forest plot using the pandas dataframe provided.

    Parameters
    ----------
    dataframe (pandas.core.frame.DataFrame)
            Pandas DataFrame where rows are variables. Columns are variable name, estimates,
            margin of error, etc.
    estimate (str)
            Name of column containing the estimates (e.g. pearson correlation coefficient,
            OR, regression estimates, etc.).
    varlabel (str)
            Name of column containing the variable label to be printed out.
    moerror (str)
            Name of column containing the margin of error in the confidence intervals.
            Should be available if 'll' and 'hl' are left empty.
    ll (str)
            Name of column containing the lower limit of the confidence intervals.
            Optional
    hl (str)
            Name of column containing the upper limit of the confidence intervals.
            Optional
    form_ci_report (bool)
            If True, form the formatted confidence interval as a string.
    ci_report (bool)
            If True, form the formatted confidence interval as a string.
    groupvar (str)
            Name of column containing group of variables.
    group_order (list-like)
            List of groups by order to report in the figure.
    annote (list-like)
            List of columns to add as additional annotation on the left-hand side of the plot.
    annoteheaders (list-like)
            List of table headers to use as column headers for the additional annotations
            on the left-hand side of the plot.
    rightannote (list-like)
            List of columns to add as additional annotation on the right-hand side of the plot.
    right_annoteheaders (list-like)
            List of table headers to use as column headers for the additional annotations
            on the right-hand side of the plot.
    pval (str)
            Name of column containing the p-values.
    starpval (bool)
            If True, use 'thresholds' and 'symbols' to "star" the p-values.
    sort (bool)
            If True, sort rows by estimate size
    sortby (str)
            Name of column to sort the dataframe by. Default is 'estimate'.
    flush (bool)
            Left-flush the variable labels.
    decimal_precision (int)
            Precision of 2 means we go from '0.1234' -> '0.12'.
    figsize (list-like):
            Figure size setting. E.g. (5,10) means width-to-height is 5 to 10.
            Size is for the dot-and-whisker plot region only. Does not control eventual
            figure size that comes from the length of the right and left y-axis ticker labels.
    xticks (list-like)
            List of xtickers to print on the x-axis.
    ylabel (str)
            Title of the left-hand side y-axis.
    xlabel (str)
            Title of the left-hand side x-axis.
    yticker2 (str)
            Name of column containing the second set of values to print on the right-hand side ytickers.
            If 'pval' is provided, then yticker2 will be set to the 'formatted_pval'.
    color_alt_rows (bool)
            If True, color alternative rows.
    preprocess (bool)
            If True, call the preprocess_dataframe() function to prepare the data for plotting.
    return_df (bool)
            If True, in addition to the Matplotlib Axes object, returns the intermediate dataframe
            created from preprocess_dataframe().
            A tuple of (preprocessed_dataframe, Ax) will be returned.

    Returns
    -------
            Matplotlib Axes object.
    """
    _local_df = dataframe.copy(deep=True)
    _local_df = check_data(
        dataframe=_local_df,
        estimate=estimate,
        varlabel=varlabel,
        moerror=moerror,
        pval=pval,
        ll=ll,
        hl=hl,
        groupvar=groupvar,
        group_order=group_order,
        annote=annote,
        annoteheaders=annoteheaders,
        rightannote=rightannote,
        right_annoteheaders=right_annoteheaders,
    )
    if (ll is None) or (hl is None):
        ll, hl = "ll", "hl"
    if ci_report is True:
        form_ci_report = True
    if preprocess:
        _local_df = _preprocess_dataframe(
            dataframe=_local_df,
            estimate=estimate,
            varlabel=varlabel,
            moerror=moerror,
            ll=ll,
            hl=hl,
            form_ci_report=form_ci_report,
            ci_report=ci_report,
            groupvar=groupvar,
            group_order=group_order,
            annote=annote,
            annoteheaders=annoteheaders,
            rightannote=rightannote,
            right_annoteheaders=right_annoteheaders,
            pval=pval,
            starpval=starpval,
            sort=sort,
            sortby=sortby,
            flush=flush,
            decimal_precision=decimal_precision,
            **kwargs,
        )
    ax = _make_forestplot(
        dataframe=_local_df,
        yticklabel="yticklabel",
        estimate=estimate,
        moerror=moerror,
        groupvar=groupvar,
        annoteheaders=annoteheaders,
        rightannote=rightannote,
        right_annoteheaders=right_annoteheaders,
        pval=pval,
        figsize=figsize,
        xticks=xticks,
        ll=ll,
        hl=hl,
        flush=flush,
        ylabel=ylabel,
        xlabel=xlabel,
        yticker2=yticker2,
        color_alt_rows=color_alt_rows,
        table=table,
        **kwargs,
    )
    return (_local_df, ax) if return_df else ax


def _preprocess_dataframe(
    dataframe: pd.core.frame.DataFrame,
    estimate: str,
    varlabel: str,
    moerror: Optional[str],
    ll: Optional[str] = None,
    hl: Optional[str] = None,
    form_ci_report: Optional[bool] = False,
    ci_report: Optional[bool] = False,
    groupvar: Optional[str] = None,
    group_order: Optional[Union[list, tuple]] = None,
    annote: Optional[Union[Sequence[str], None]] = None,
    annoteheaders: Optional[Union[Sequence[str], None]] = None,
    rightannote: Optional[Union[Sequence[str], None]] = None,
    right_annoteheaders: Optional[Union[Sequence[str], None]] = None,
    capitalize: str = "capitalize",
    pval: Optional[str] = None,
    starpval: bool = True,
    sort: bool = False,
    sortby: Optional[str] = None,
    sortascend: bool = True,
    flush: bool = True,
    decimal_precision: int = 2,
    **kwargs: Any,
) -> pd.core.frame.DataFrame:
    """
    Preprocess the dataframe to be ready for plotting.

    Returns
    -------
            pd.core.frame.DataFrame with additional columns for plotting.
    """
    if (groupvar is not None) and (group_order is not None):
        if sort is True:
            list(group_order).reverse()
        dataframe = sort_groups(dataframe, groupvar=groupvar, group_order=group_order)
    dataframe = sort_data(
        dataframe=dataframe,
        estimate=estimate,
        groupvar=groupvar,
        sort=sort,
        sortby=sortby,
        sortascend=sortascend,
    )
    if groupvar is not None:  # Make groups
        dataframe = normalize_varlabels(
            dataframe=dataframe, varlabel=groupvar, capitalize=capitalize
        )
        dataframe = insert_groups(dataframe=dataframe, groupvar=groupvar, varlabel=varlabel)
    dataframe = normalize_varlabels(
        dataframe=dataframe, varlabel=varlabel, capitalize=capitalize
    )
    dataframe = indent_nongroupvar(dataframe=dataframe, varlabel=varlabel, groupvar=groupvar)
    if form_ci_report:
        dataframe = form_est_ci(
            dataframe=dataframe,
            estimate=estimate,
            moerror=moerror,
            ll=ll,
            hl=hl,
            decimal_precision=decimal_precision,
        )
    dataframe = star_pval(
        dataframe=dataframe,
        pval=pval,
        starpval=starpval,
        decimal_precision=decimal_precision,
    )
    if annote is None:  # Form ytickers = formatted variable labels
        dataframe = format_varlabels(
            dataframe=dataframe,
            varlabel=varlabel,
            form_ci_report=form_ci_report,
            ci_report=ci_report,
            groupvar=groupvar,
        )
    else:
        dataframe = prep_annote(
            dataframe=dataframe,
            groupvar=groupvar,
            varlabel=varlabel,
            annote=annote,
            annoteheaders=annoteheaders,
            **kwargs,
        )
    if rightannote is not None:
        dataframe = prep_rightannnote(
            dataframe=dataframe,
            groupvar=groupvar,
            varlabel=varlabel,
            rightannote=rightannote,
            right_annoteheaders=right_annoteheaders,
        )
    dataframe = make_tableheaders(
        dataframe=dataframe,
        varlabel=varlabel,
        annote=annote,
        annoteheaders=annoteheaders,
        rightannote=rightannote,
        right_annoteheaders=right_annoteheaders,
        **kwargs,
    )
    return reverse_dataframe(dataframe)  # since plotting starts from bottom


def _make_forestplot(
    dataframe: pd.core.frame.DataFrame,
    yticklabel: str,
    estimate: str,
    moerror: str,
    groupvar: str,
    pval: str,
    xticks: Optional[Union[list, range]],
    ll: str,
    hl: str,
    flush: bool,
    annoteheaders: Optional[Union[Sequence[str], None]],
    rightannote: Optional[Union[Sequence[str], None]],
    right_annoteheaders: Optional[Union[Sequence[str], None]],
    ylabel: str,
    xlabel: str,
    yticker2: Optional[str],
    color_alt_rows: bool,
    figsize: Union[Tuple, List],
    despine: bool = True,
    table: bool = False,
    **kwargs: Any,
) -> Axes:
    """
    Draw the forest plot.

    Returns
    -------
            Matplotlib Axes object.
    """
    _, ax = plt.subplots(figsize=figsize, facecolor="white")
    if moerror is None:
        moerror = "moerror"
    ax = draw_ci(
        dataframe=dataframe,
        estimate=estimate,
        yticklabel=yticklabel,
        moerror=moerror,
        ax=ax,
        **kwargs,
    )
    draw_est_markers(
        dataframe=dataframe, estimate=estimate, yticklabel=yticklabel, ax=ax, **kwargs
    )
    format_xticks(dataframe=dataframe, ll=ll, hl=hl, xticks=xticks, ax=ax, **kwargs)
    draw_ref_xline(
        ax=ax,
        dataframe=dataframe,
        annoteheaders=annoteheaders,
        right_annoteheaders=right_annoteheaders,
        **kwargs,
    )
    pad = right_flush_yticklabels(
        dataframe=dataframe, yticklabel=yticklabel, flush=flush, ax=ax, **kwargs
    )
    if rightannote is None:
        ax, righttext_width = draw_pval_right(
            dataframe=dataframe,
            pval=pval,
            annoteheaders=annoteheaders,
            rightannote=rightannote,
            yticklabel=yticklabel,
            yticker2=yticker2,
            pad=pad,
            ax=ax,
            **kwargs,
        )
    else:
        ax, righttext_width = draw_yticklabel2(
            dataframe=dataframe,
            annoteheaders=annoteheaders,
            right_annoteheaders=right_annoteheaders,
            ax=ax,
            **kwargs,
        )

    draw_ylabel1(ylabel=ylabel, pad=pad, ax=ax, **kwargs)
    remove_ticks(ax)
    format_grouplabels(dataframe=dataframe, groupvar=groupvar, ax=ax, **kwargs)
    format_tableheader(
        annoteheaders=annoteheaders, right_annoteheaders=right_annoteheaders, ax=ax, **kwargs
    )
    despineplot(despine=despine, ax=ax)
    format_xlabel(xlabel=xlabel, ax=ax, **kwargs)
    if color_alt_rows:
        draw_alt_row_colors(
            dataframe,
            groupvar=groupvar,
            annoteheaders=annoteheaders,
            right_annoteheaders=right_annoteheaders,
            ax=ax,
        )
    if (annoteheaders is not None) or (
        (pval is not None) or (right_annoteheaders is not None)
    ):
        if table:
            draw_tablelines(
                dataframe=dataframe,
                righttext_width=righttext_width,
                pval=pval,
                right_annoteheaders=right_annoteheaders,
                ax=ax,
            )
    return ax
