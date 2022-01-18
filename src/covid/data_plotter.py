import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io

import seaborn as sns
from typing import Any, Optional
from loguru import logger 

from covid.data_getter import CovidSQLGetter


"""
def plot_dynamics(data: pd.DataFrame) -> Any:
    
    fig = Figure(constrained_layout=True)
    subplot = fig.subplots()
    sns.lineplot(data=data, x="report_date", y="conformed_daily", ax=subplot)
    sns.despine(fig=fig)
    bio = BytesIO()
    bio.name = 'plot.png'
    fig.savefig(bio, bbox_inches='tight')
    bio.seek(0)
    return bio
"""

class CovidPlotter:
    
    def __init__(self, 
                 covid_getter: CovidSQLGetter) -> None:
        
        self.covid_getter = covid_getter

    @staticmethod
    def _prepare_data_outlier_deaths(data: pd.DataFrame, threshhold: int = 60_000) -> pd.DataFrame:
        data = data.copy()
        data.loc[data["deaths_daily"] > threshhold, "deaths_daily"] = np.nan
        return data
        
    @staticmethod
    def _prepare_data_outlier(data: pd.DataFrame, data_name: str) -> pd.DataFrame:
        
        config_threshhold = {
            "deaths": 100_000,
            "existing": 6_000_000
        }
        threshhold_ = config_threshhold.get(data_name)
        if threshhold_ is not None:
            data = data.copy()          
            col_name = data_name + "_daily"   
            data.loc[data[col_name] > threshhold_, col_name] = np.nan
            return data
        else:
            return data
           
    @staticmethod
    def _prepare_plot(plot):
        fig = plot.get_figure()
        fig.tight_layout()
        image = io.BytesIO()
        fig.savefig(image, format="png", dpi=300)
        plt.close(fig)
        image.seek(0)
        return image
          
    def create_world_dynamics_plot(self, data_name: str = "confirmed"):
    
        # world dynamics
        data = self.covid_getter.get_world_stat()
        data = CovidPlotter._prepare_data_outlier(data=data, data_name=data_name)
        
        # create_plot
        plot = sns.lineplot(data=data, x="report_date", y=data_name+"_daily")
        
        # save plot
        image = CovidPlotter._prepare_plot(plot=plot)
        
        logger.opt(ansi=True).debug(f"Create world dynamic plot for <green>{data_name.upper()}</green>")
        return image
    
    def create_ukraine_dynamics_plot(self, data_name: str = "confirmed"):
        
        data: pd.DataFrame = self.covid_getter.get_ukraine_agg_stat()
        #data_vaccine: pd.DataFrame = self.covid_getter.get_vaccine_agg_stat()
        
        #data = pd.concat([data, data_vaccine], axis=1)
        
        # create_plot
        plot = sns.lineplot(data=data, x="report_date", y=data_name+"_daily")
        # save plot
        image = CovidPlotter._prepare_plot(plot=plot)
        
        logger.opt(ansi=True).debug(f"Create Ukraine dynamic plot for <green>{data_name.upper()}</green>")
        return image
    