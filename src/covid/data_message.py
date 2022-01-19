from os import stat
from typing import List, Optional
from covid.data_getter import CovidSQLGetter
import flag
import numpy as np
import pandas as pd
from columnar import columnar
import aiogram.utils.markdown as md
from aiogram.utils import emoji
from loguru import logger


class TelegramMessageCovidText:
    
    def __init__(self, covid_getter: CovidSQLGetter) -> None:
        self.covid_getter = covid_getter

    @staticmethod
    def _prepare_df_top_country_for_last_date(data: pd.DataFrame, data_name: str = "confirmed", top_n: int = 20) -> pd.DataFrame:
                  
        column_select = ["country_name_flag", "country_name", f"{data_name}_daily", f"{data_name}_daily_percent"]
        data = data.loc[:, column_select].copy()
        data = data \
            .fillna({"country_name_flag": "", f"{data_name}_daily_percent": 0}) \
            .replace(np.inf, 0) \
            .nlargest(n=top_n, columns=[f"{data_name}_daily"])
            #.sort_values(by=[f"{data_name}_daily"], ascending=True) 
            
        data[f"{data_name}_daily"] = \
            data[f"{data_name}_daily"].apply(lambda row: f"{int(row): ,}".replace(",", " ") )
        data[f"{data_name}_daily_percent"] = \
            (100 * data[f"{data_name}_daily_percent"]).round(0).astype(int).astype(str) + "%"
        data[f"{data_name}_daily_percent"] = \
            data[f"{data_name}_daily_percent"].apply(lambda row: "+" + row if row[0] != "-" else row)
            
        return data

    @staticmethod
    def _prepare_df_all_ukr_regions_for_last_date(data: pd.DataFrame) -> pd.DataFrame:
        
        column_select = ["region_name", "confirmed_daily", "confirmed_daily_percent"]
        data = data.loc[:, column_select].copy()
        data = data.fillna({"confirmed_daily_percent": 0}).replace(np.inf, 0) 
        data = data.sort_values(by="confirmed_daily", ascending=False)
            
        data["confirmed_daily"] = \
            data["confirmed_daily"].apply(lambda row: f"{int(row): ,}".replace(",", " ") )
        data["confirmed_daily_percent"] = \
            (100 * data["confirmed_daily_percent"]).round(0).astype(int).astype(str) + "%"
        data["confirmed_daily_percent"] = \
            data["confirmed_daily_percent"].apply(lambda row: "+" + row if row[0] != "-" else row)
            
        return data
        
    @staticmethod
    def _prepare_msg_top_country_for_last_date(data: pd.DataFrame, headers: List[str]) -> str:
        
        data = data.copy()
        data_list = data.values.tolist()        
        for rank_, row_ in enumerate(data_list, start=1):
            row_[0] = flag.flag(row_[0]) if row_[0] != " " else row_[0]
            row_[0] += f" ({str(rank_)}) " + row_[1]
            del row_[1]
        result = columnar(data_list, no_borders=True, headers=headers)
        return result

    @staticmethod
    def _prepare_msg_all_ukr_regions_for_last_date(data: pd.DataFrame, headers: Optional[List[str]] = None) -> str:
        
        data = data.copy()
        data_list = data.values.tolist()        
        result = columnar(data_list, no_borders=True, headers=headers)
        return result
                       
    def get_message_top_country_for_last_date(self, top_n: int = 20, data_name: str = "confirmed") -> str:
        
        config_ = {
            "confirmed": {"head": "НОВІ ВИПАДКИ", "msg": "нових випадках"},
            "deaths": {"head": "СМЕРТІ", "msg": "кількості смертей від"},
            "existing": {"head": "ХВОРІЮТЬ", "msg": "кількості тих, хто продовжує хворіти від"}
        }
        config_msg = config_.get(data_name)
        
        # load data
        data_country = self.covid_getter.get_country_stat(is_last_date=True)
        last_date = data_country["report_date"].unique()[0].strftime("%Y-%m-%d")
        
        # prepare data frame and final output message
        headers_table = ["Країна", "К-сть", "Приріст"]
        data_country = TelegramMessageCovidText._prepare_df_top_country_for_last_date(data=data_country, data_name=data_name, top_n=top_n)
        result = TelegramMessageCovidText._prepare_msg_top_country_for_last_date(data=data_country, headers=headers_table)

        headers_message = f"{config_msg.get('head')}. СВІТ. \nТоп {top_n} країн по {config_msg.get('msg')} covid-19 за "
        result = \
            headers_message + \
            last_date + ":" + "\n" + \
            "```" + \
            result + \
            "``` \n" + \
            "Дані: https://covid19.rnbo.gov.ua/" 
        
        logger.opt(ansi=True).debug(f"Send message with table Top Country with <green>{data_name.upper()}</green> covid data")      
        return result

    def get_message_all_ukr_regions_for_last_date(self, top_n: Optional[int] = None) -> str:
        
        
        # load data
        data = self.covid_getter.get_ukraine_stat(is_last_date=True, top_n=top_n)
        confirm_total = int(data.confirmed_daily.sum())
        
        last_date = data["report_date"].unique()[0].strftime("%Y-%m-%d")
        # prepare data frame and final output message
        headers_table = ["Область", "К-сть", "Приріст"]    
        data = TelegramMessageCovidText._prepare_df_all_ukr_regions_for_last_date(data=data)
        result = TelegramMessageCovidText._prepare_msg_all_ukr_regions_for_last_date(data=data, headers=headers_table)
    
        headers_message = f"НОВІ ВИПАДКИ. УКРАЇНА. \nОбласті України по нових випадках covid-19 за "
        result = \
            headers_message + \
            last_date + ":" + "\n" + \
            "```" + \
            result + \
            "\n" + \
            f"Загалом по Україні {confirm_total:,}".replace(",", " ") + "\n" + \
            "``` \n" + \
            "Дані: https://covid19.rnbo.gov.ua/"   
        return result    
    
    def get_message_ukr_vaccine_for_last_date(self, top_n: Optional[int] = None) -> str:
        
        data = self.covid_getter.get_vaccine_stat(is_last_date=True)
        last_date = data["report_date"].unique()[0].strftime("%Y-%m-%d")
        
        data = data \
            .groupby(by=["region_name", "dose_name"], as_index=False) \
            .agg(count_vaccine=('count_vaccine', 'sum'))
        data["count_vaccine"] = data["count_vaccine"] \
            .apply(lambda row: f"{int(row): ,}".replace(",", " ") )
        data = data \
            .pivot(index="region_name", columns="dose_name", values="count_vaccine" ) \
            .reset_index()
        data = data \
            .sort_values(by=[2], ascending=False)
        
        headers_table = ["Область"] + [str(i) for i in range(1, data.columns.shape[0])]
        result = columnar(data.values.tolist(), no_borders=True, headers=headers_table)
        
        headers_message = f"ВАКЦИНАЦІЯ. \nК-сть вакцинацій по номеру дози за {last_date}: \n"
        message = \
            headers_message + \
            "``` \n" + \
            result + "\n" + \
            "``` \n"
        return message
    
    def get_message_ukraine_main(self, add_regions: bool = True) -> str:
        
        
        # last date in database
        _, last_date = self.covid_getter.get_last_date()
        # cumulative data for Ukraine: sum region data
        df_ukraine_stat = self.covid_getter.get_ukraine_stat(is_last_date=True)
        df_ukraine_stat_agg = df_ukraine_stat.loc[:, ["confirmed", "deaths", "recovered", "existing"]].sum()
        df_ukraine_stat_daily = df_ukraine_stat.loc[:, ["confirmed_daily", "deaths_daily", "recovered_daily", "existing_daily"]].sum()
                
        # prepare data for Ukraine regions 
        df_ukraine_stat = TelegramMessageCovidText._prepare_df_all_ukr_regions_for_last_date(data=df_ukraine_stat)
        df_ukraine_stat = TelegramMessageCovidText._prepare_msg_all_ukr_regions_for_last_date(data=df_ukraine_stat, headers=None)
        
        # ukraine vaccines data by regions
        df_ukraine_stat_vaccines = self.covid_getter.get_vaccine_stat(is_last_date=True)
        df_ukraine_stat_vaccines_agg = df_ukraine_stat_vaccines \
            .groupby(by=["dose_name"])["count_vaccine_cum"].sum()
        df_ukraine_stat_vaccines_daily = df_ukraine_stat_vaccines \
            .groupby(by=["dose_name"])["count_vaccine"].sum()
        
        result = \
            md.text(
                last_date.strftime("%d.%m.%Y"), ":\n\n",
                md.bold("За весь час пандемії в Україні:\n"),
                emoji.emojize(":large_orange_diamond:"), f"захворіло - {int(df_ukraine_stat_agg['confirmed']):,}".replace(",", " "), ";\n",
                emoji.emojize(":large_orange_diamond:"), f"померло - {int(df_ukraine_stat_agg['deaths']):,}".replace(",", " "), ";\n",
                emoji.emojize(":large_orange_diamond:"), f"одужало - {int(df_ukraine_stat_agg['recovered']):,}".replace(",", " "), ";\n\n",
                
                emoji.emojize(":large_orange_diamond:"), f"отримало {emoji.emojize(':one:')} дозу вакцини - {df_ukraine_stat_vaccines_agg[1]:,};\n".replace(",", " "),
                emoji.emojize(":large_orange_diamond:"), f"отримало {emoji.emojize(':two:')} дозу вакцини - {df_ukraine_stat_vaccines_agg[2]:,};\n".replace(",", " "),
                emoji.emojize(":large_orange_diamond:"), f"отримали {emoji.emojize(':three:')} дозу вакцини - {df_ukraine_stat_vaccines_agg[3]:,}.\n\n\n".replace(",", " "),
                
                md.bold("За останню добу в Україні: \n"),
                emoji.emojize(":large_blue_diamond:"), f"захворіло - {int(df_ukraine_stat_daily['confirmed_daily']):,}".replace(",", " "), ",\n",
                emoji.emojize(":large_blue_diamond:"), f"померло - {int(df_ukraine_stat_daily['deaths_daily']):,}".replace(",", " "), ",\n",
                emoji.emojize(":large_blue_diamond:"), f"одужало - {int(df_ukraine_stat_daily['recovered_daily']):,}".replace(",", " "), ",\n\n",
                
                emoji.emojize(":large_blue_diamond:"), f"отримало {emoji.emojize(':one:')} дозу вакцини - {df_ukraine_stat_vaccines_daily[1]:,};\n".replace(",", " "),
                emoji.emojize(":large_blue_diamond:"), f"отримало {emoji.emojize(':two:')} дозу вакцини - {df_ukraine_stat_vaccines_daily[2]:,};\n".replace(",", " "),
                emoji.emojize(":large_blue_diamond:"), f"отримали {emoji.emojize(':three:')} дозу вакцини - {df_ukraine_stat_vaccines_daily[3]:,}.\n\n"                
            )
        
        if add_regions:
            result = \
                md.text(
                    result,
                    md.bold("За останню добу виявлено нових випадків в регіонах України:\n"),
                    "```", df_ukraine_stat, "```" 
                )
        
        result = \
            md.text(
                result,
                "Джерела: \n https://covid19.rnbo.gov.ua/,\n https://health-security.rnbo.gov.ua/vaccination"
            )       
        
        logger.opt(ansi=True).debug("Send main message for Ukraine covid statistics")
        
        return result
