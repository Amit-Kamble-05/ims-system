import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from courses.models import Course, CourseContent


class Command(BaseCommand):
    help = "Sync courses from CSV using pandas"

    def handle(self, *args, **kwargs):

        csv_path = Path(settings.BASE_DIR) / "data" / "Courses Details.csv"

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR("CSV file not found"))
            return

        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():

            course_name = row["Course Name"].strip()
            content = row["Course Content"].strip()
            fees = row["Fees"]
            duration = row["Duration"].strip()

            # Create or update course
            course, created = Course.objects.update_or_create(
                name=course_name,
                defaults={
                    "total_fees": fees,
                    "duration": duration
                }
            )

            # Add course content if not exists
            CourseContent.objects.get_or_create(
                course=course,
                content_name=content
            )

        self.stdout.write(self.style.SUCCESS("Courses synced successfully"))