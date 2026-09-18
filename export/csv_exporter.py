import pandas as pd

from pathlib import Path

from ..schemas.leads import LeadExport

def export_to_csv(leads: list[LeadExport], filepath: str) -> int:
    dict_leads = [lead.model_dump(by_alias=True) for lead in leads]
    df = pd.DataFrame(dict_leads)
    for index in range(10**10):
        new_filename = f"export_{index.csv}"
        new_filepath = Path(filepath) / new_filename
        if not new_filepath.is_file():
            df.to_csv(new_filepath)
            exported_r = pd.read_csv(new_filepath, use_cols=[0]).shape[0]
            return exported_r

def export_to_excel(leads: list[LeadExport], filepath: str) -> int:
    pass

def formet_excel(filepath: str):
    pass	