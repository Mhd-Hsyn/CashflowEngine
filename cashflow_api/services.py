import io
import pandas as pd
from django.db import transaction
from django.core.files.base import ContentFile
from decimal import Decimal, InvalidOperation
from .models import (
    MortalityRate, 
    JobAssumption,
    EmployeeProjection,
    CalculationJob,
)
from core.constants.choices import JobStatusChoices
from core.utils.helpers import to_decimal


class MortalityRateService:
    
    @staticmethod
    def import_mortality_table(file_obj):
        try:
            df = pd.read_csv(file_obj)
            df.columns = df.columns.str.strip().str.lower()
            
            required_columns = ['age', 'qx', 'px']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")

            with transaction.atomic():
                for _, row in df.iterrows():
                    clean_qx = to_decimal(row['qx'])
                    clean_px = to_decimal(row['px'])

                    MortalityRate.objects.update_or_create(
                        age=int(row['age']),
                        defaults={
                            'qx_percent': clean_qx * 100, 
                            'px_percent': clean_px * 100,
                            'qx_value': clean_qx,
                            'px_value': clean_px
                        }
                    )
            
            return f"Successfully processed {len(df)} rows."

        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")


class CalculationEngine:
    
    REQUIRED_KEYS = {
        'valuation_date', 
        'discount_rate', 
        'salary_increase_rate', 
        'retirement_age'
    }

    def __init__(self, job_id):
        self.job = CalculationJob.objects.get(id=job_id)

    def _extract_assumptions(self):
        df = pd.read_csv(self.job.assumptions_file, header=None)
        data_map = {}
        for _, row in df.iterrows():
            if pd.notna(row[0]):
                key = str(row[0]).strip().lower().replace(' ', '_')
                val = row[1]
                data_map[key] = val

        missing = self.REQUIRED_KEYS - data_map.keys()
        if missing:
            raise ValueError(f"Missing required assumptions: {', '.join(missing)}")

        return JobAssumption.objects.create(
            job=self.job,
            valuation_date=pd.to_datetime(data_map['valuation_date']).date(),
            discount_rate=to_decimal(data_map['discount_rate']),
            salary_increase_rate=to_decimal(data_map['salary_increase_rate']),
            retirement_age=int(data_map['retirement_age'])
        )

    def run(self):
        try:
            self.job.status = JobStatusChoices.PROCESSING
            self.job.save()

            assumptions = self._extract_assumptions()
            
            retire_age = assumptions.retirement_age
            inc_rate = assumptions.salary_increase_rate
            valuation_year = assumptions.valuation_date.year

            employees_df = pd.read_csv(self.job.input_file)
            employees_df.columns = employees_df.columns.str.strip().str.lower()
            
            self.job.total_input_rows = len(employees_df)

            mortality_lookup = {
                m.age: m.qx_value for m in MortalityRate.objects.all()
            }

            projection_db_objects = []
            csv_results = []

            for _, emp in employees_df.iterrows():
                emp_id = emp.get('emp_id')
                emp_name = emp.get('emp_name', '')
                birth_date = pd.to_datetime(emp.get('date_birth'))
                
                current_salary = to_decimal(emp.get('salary'))
                
                current_age = valuation_year - birth_date.year
                temp_salary = current_salary

                for age in range(current_age, retire_age + 1):
                    qx = mortality_lookup.get(age, Decimal("0.00"))
                    expected_outflow = temp_salary * qx
                    
                    csv_results.append({
                        'Emp ID': emp_id,
                        'Name': emp_name,
                        'Year/Age': age,
                        'Projected Salary': round(temp_salary, 2),
                        'Probability (qx)': round(qx, 6),
                        'Expected Outflow': round(expected_outflow, 2)
                    })

                    projection_db_objects.append(EmployeeProjection(
                        job=self.job,
                        emp_id=emp_id,
                        emp_name=emp_name,
                        year=age,
                        projected_salary=temp_salary,
                        probability_qx=qx,
                        expected_outflow=expected_outflow
                    ))

                    temp_salary = temp_salary * (1 + inc_rate)

            EmployeeProjection.objects.bulk_create(projection_db_objects, batch_size=5000)

            output_df = pd.DataFrame(csv_results)
            csv_buffer = io.BytesIO()
            output_df.to_csv(csv_buffer, index=False)
            
            self.job.output_file.save(
                f"result_job_{self.job.id}.csv", 
                ContentFile(csv_buffer.getvalue()), 
                save=False
            )
            
            self.job.total_output_rows = len(output_df)
            self.job.status = JobStatusChoices.COMPLETED
            self.job.save()

        except Exception as e:
            self.job.status = JobStatusChoices.FAILED
            self.job.error_message = str(e)
            self.job.save()
            raise e


