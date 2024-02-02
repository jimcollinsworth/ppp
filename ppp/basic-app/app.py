from pathlib import Path

import pandas as pd
from pandas.api.types import CategoricalDtype

import matplotlib.pyplot as plt
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo

sns.set(style="darkgrid")

app_ui = ui.page_navbar(
    ui.nav_panel("Data", 
        ui.panel_title("PPP Loan data from SBA"),
        ui.input_file("file1", "Choose PPO CSV File", accept=[".csv"], multiple=False),
        ui.output_data_frame("summary_statistics"),
        ui.panel_main(
            ui.output_plot("histogram"),
        )
    ), 
    ui.nav_panel("pandas", 
        ui.output_data_frame("pandas_info"),
    ),
    ui.nav_panel("Detailed Profiler",
        ui.panel_main(
            ui.HTML("<strong>open('..\\output.html').read()</strong>")
        ),
    ), 
    title="PPP Loan data from SBA", 
    id="navbar", 
    position="fixed-top",
    fillable=True 
) 

def load_df(file_name: str) -> pd.DataFrame:
    # define columns for PPP FOIA file https://data.sba.gov/dataset/ppp-foia
    dtype={
        "LoanNumber": "int64",
        "SBAOfficeCode": "category",
        "ProcessingMethod": "category",
        "BorrowerName": "string",
        "BorrowerAddress": "string",
        "BorrowerCity": "string",
        "BorrowerState": "category",
        "BorrowerZip": "category",
        "LoanStatus": "category",
        "Term": "category",
        "SBAGuarantyPercentage": "int64",
        "InitialApprovalAmount": "float64",
        "CurrentApprovalAmount": "float64",
        "UndisbursedAmount": "float64",
        "FranchiseName": "string",
        "ServicingLenderLocationID" : "int64",
        "ServicingLenderName": "string",
        "ServicingLenderAddress": "string",
        "ServicingLenderCity": "string",
        "ServicingLenderState":  'category',
        "ServicingLenderZip":  'category',
        "RuralUrbanIndicator":  'category',
        "HubzoneIndicator":  'category',
        "LMIIndicator":  'category',
        "BusinessAgeDescription":  'category',
        "ProjectCity":  'string',
        "ProjectCountyName":  'string',
        "ProjectState":  'category',
        "ProjectZip":  'category',
        "CD":  'string',
        "JobsReported":  'string',
        "NAICSCode":  'string',
        "Race":  'category',
        "Ethnicity":  'category',
    #       "UTILITIES_PROCEED":  'float64',
    #       "PAYROLL_PROCEED":  'float64',
    #       "MORTGAGE_INTEREST_PROCEED":  'float64',
    #       "RENT_PROCEED":  'float64',
    #       "REFINANCE_EIDL_PROCEED":  'float64',
    #       "HEALTH_CARE_PROCEED":  'float64',
    #       "DEBT_INTEREST_PROCEED":  'float64',
        "BusinessType":  'string',
        "OriginatingLenderLocationID":  'string',
        "OriginatingLender":  'string',
        "OriginatingLenderCity":  'string',
        "OriginatingLenderState":  'category',
        "Gender":  'category',
        "Veteran":  'category',
        "NonProfit":  'category',
        "ForgivenessAmount":  'float64'
    }
    parse_dates = ["DateApproved", "ForgivenessDate", "LoanStatusDate"]

    df = pd.read_csv(
        #"E:\\data\\ppp\\public_up_to_150k_5_230930.csv",
        Path(__file__).parent / file_name,
        #parse_dates=parse_dates,  # seems to pick out dates fine without this, 
        dtype=dtype,
        na_values="NA")

    print(df.info())
    print(df.dtypes)
    print(f"{df['BorrowerState']}{df['ProcessingMethod']}")
    
    return df

# global for now, where should the big df go for Shiny? in server?
df = reactive.value()

def server(input: Inputs, output: Outputs, session: Session):

    @reactive.Effect
    def parsed_file():
        file: list[FileInfo] | None = input.file1()
        if file is None:
            pass
        else:
            df.set(load_df(file[0]["datapath"]))

    @output
    @render.data_frame
    def summary_statistics():
    
        display_df = df()[
            [
                "LoanNumber","DateApproved","SBAOfficeCode",
                "ProcessingMethod","BorrowerName","BorrowerAddress",
                "BorrowerCity","BorrowerState","BorrowerZip",
                "LoanStatusDate","LoanStatus","Term",
                "SBAGuarantyPercentage","InitialApprovalAmount","CurrentApprovalAmount",
                "UndisbursedAmount","FranchiseName","ServicingLenderLocationID",
                "ServicingLenderName","ServicingLenderAddress","ServicingLenderCity",
                "ServicingLenderState","ServicingLenderZip","RuralUrbanIndicator",
                "HubzoneIndicator","LMIIndicator","BusinessAgeDescription",
                "ProjectCity","ProjectCountyName","ProjectState",
                "ProjectZip","CD","JobsReported","NAICSCode",
                "Race","Ethnicity",
                #"UTILITIES_PROCEED",
                #"PAYROLL_PROCEED","MORTGAGE_INTEREST_PROCEED","RENT_PROCEED",
                #"REFINANCE_EIDL_PROCEED","HEALTH_CARE_PROCEED","DEBT_INTEREST_PROCEED",
                "BusinessType","OriginatingLenderLocationID","OriginatingLender",
                "OriginatingLenderCity","OriginatingLenderState","Gender",
                "Veteran","NonProfit","ForgivenessAmount",
                "ForgivenessDate"
            ]
        ]
        return render.DataGrid(display_df, filters=True)

    @output
    @render.plot
    def histogram():
        sns.histplot(data=df(), x='CurrentApprovalAmount')

    @output
    @render.ui
    def pandas_info():
        pass

app = App(app_ui, server)
