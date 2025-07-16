import pandas as pd
from django.core.management.base import BaseCommand
from tickets.models import StudentRecord

class Command(BaseCommand):
    help = 'Import or update student/staff records from Excel'

    def handle(self, *args, **kwargs):
        file_path = 'SchoolDatabase.xlsx'
        try:
            df = pd.read_excel(file_path)

            # Clean column headers (remove trailing spaces)
            df.columns = [col.strip().upper() for col in df.columns]

            count = 0
            for _, row in df.iterrows():
                try:
                    StudentRecord.objects.update_or_create(
                        id_number=str(row['ID NUMBER']).strip().upper(),
                        defaults={
                            'first_name': str(row['FIRST NAME']).strip().title(),
                            'surname': str(row['LAST NAME']).strip().title(),
                            'department': str(row['DEPARTMENT']).strip().upper(),
                            'office': str(row.get('OFFICE', '') or '').strip(),
                            'level': str(row.get('LEVEL', '') or '').strip(),
                            'status': str(row.get('STATUS', '') or '').strip(),
                        }
                    )
                    count += 1
                except Exception as e:
                    print(f"Skipped row due to error: {e}")

            
            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported/updated {count} student/staff records."
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
