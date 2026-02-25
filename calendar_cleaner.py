import os
import logging
from icalendar import Calendar

logger = logging.getLogger('urnik.cleaner')


def clean_ics_file(input_file, output_file, excluded_groups=None):
    """Removes events containing excluded groups in the description from an .ics file."""
    if excluded_groups is None:
        excluded_groups = ['RV1', 'Erasmus']

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r', encoding='utf-8') as f:
        calendar = Calendar.from_ical(f.read())

    cleaned_calendar = Calendar()

    for key, value in calendar.items():
        cleaned_calendar.add(key, value)

    kept = 0
    excluded = 0

    for component in calendar.walk():
        if component.name == 'VEVENT':
            description = component.get('DESCRIPTION', '').replace('\\,', ',').replace('\\n', ' ').strip()

            # Check if any excluded group is in the description
            if any(excluded_group in description for excluded_group in excluded_groups):
                excluded += 1
                continue

            summary = component.get('SUMMARY', 'No Title')
            if ' RV' in description:
                new_summary = summary  + ' - RV'
            elif ' PR' in description:
                new_summary = summary  + ' - PR'
            elif ' SV' in description:
                new_summary = summary  + ' - SV'
            elif ' LV' in description:
                new_summary = summary  + ' - LV'
            else:
                new_summary = summary
            component['SUMMARY'] = new_summary
            cleaned_calendar.add_component(component)
            kept += 1

    with open(output_file, 'wb') as f:
        f.write(cleaned_calendar.to_ical())

    logger.info('Cleaned calendar saved to %s (kept %d, excluded %d events)', output_file, kept, excluded)


def merge_and_clean_ics_files(input_files, output_file, excluded_groups=None):
    """Merge multiple .ics files into one, applying exclusion and summary annotation.

    Args:
        input_files: List of paths to .ics files to merge.
        output_file: Path to write the merged+cleaned .ics file.
        excluded_groups: List of strings; events whose description contains
                         any of these strings will be excluded.
    """
    if excluded_groups is None:
        excluded_groups = ['RV1', 'Erasmus']

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    merged_calendar = Calendar()
    header_copied = False
    total_kept = 0
    total_excluded = 0

    for input_file in input_files:
        logger.debug('Reading: %s', input_file)
        with open(input_file, 'r', encoding='utf-8') as f:
            calendar = Calendar.from_ical(f.read())

        # Copy calendar-level properties from the first file only
        if not header_copied:
            for key, value in calendar.items():
                merged_calendar.add(key, value)
            header_copied = True

        kept = 0
        excluded = 0

        for component in calendar.walk():
            if component.name == 'VEVENT':
                description = component.get('DESCRIPTION', '').replace('\\,', ',').replace('\\n', ' ').strip()

                # Check if any excluded group is in the description
                if any(excluded_group in description for excluded_group in excluded_groups):
                    excluded += 1
                    continue

                summary = component.get('SUMMARY', 'No Title')
                if ' RV' in description:
                    new_summary = summary + ' - RV'
                elif ' PR' in description:
                    new_summary = summary + ' - PR'
                elif ' SV' in description:
                    new_summary = summary + ' - SV'
                elif ' LV' in description:
                    new_summary = summary + ' - LV'
                else:
                    new_summary = summary
                component['SUMMARY'] = new_summary
                merged_calendar.add_component(component)
                kept += 1

        logger.info('Processed %s: kept %d, excluded %d events', input_file, kept, excluded)
        total_kept += kept
        total_excluded += excluded

    with open(output_file, 'wb') as f:
        f.write(merged_calendar.to_ical())

    logger.info('Merged & cleaned calendar saved to %s (%d sources, %d events kept, %d excluded)',
                output_file, len(input_files), total_kept, total_excluded)
