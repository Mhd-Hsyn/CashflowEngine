import pandas as pd
from django.db import transaction
from decimal import Decimal, InvalidOperation
from .models import MortalityRate

class MortalityRateService:
    
    @staticmethod
    def parse_decimal(value):
        if pd.isna(value):
            return Decimal("0.00")
        clean_val = str(value).strip().replace('%', '')
        try:
            return Decimal(clean_val)
        except InvalidOperation:
            return Decimal("0.00")

    @staticmethod
    def import_mortality_table(file_obj):
        try:
            df = pd.read_csv(file_obj)
            df.columns = df.columns.str.strip()
            required_columns = ['age', 'qx', 'px']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")

            with transaction.atomic():
                for _, row in df.iterrows():
                    raw_qx = MortalityRateService.parse_decimal(row['qx'])
                    raw_px = MortalityRateService.parse_decimal(row['px'])

                    MortalityRate.objects.update_or_create(
                        age=int(row['age']),
                        defaults={
                            'qx_percent': raw_qx,
                            'px_percent': raw_px,
                            'qx_value': raw_qx / Decimal(100),
                            'px_value': raw_px / Decimal(100)
                        }
                    )
            
            return f"Successfully processed {len(df)} rows."

        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

