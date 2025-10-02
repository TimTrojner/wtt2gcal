import os
from icalendar import Calendar

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

    for component in calendar.walk():
        if component.name == 'VEVENT':
            description = component.get('DESCRIPTION', '').replace('\\,', ',').replace('\\n', ' ').strip()

            # Check if any excluded group is in the description
            if any(excluded_group in description for excluded_group in excluded_groups):
                continue

            summary = component.get('SUMMARY', 'No Title')
            if 'RV' in description:
                new_summary = summary  + ' - RV'
            else:
                new_summary = summary  + ' - PR'
            component['SUMMARY'] = new_summary
            cleaned_calendar.add_component(component)

    with open(output_file, 'wb') as f:
        f.write(cleaned_calendar.to_ical())

    print(f'✅ Cleaned calendar saved to {output_file}')
