import os
from icalendar import Calendar

def clean_ics_file(input_file, output_file):
    """Removes events containing 'RV1' in the description from an .ics file."""

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

            if 'RV1' in description or 'Erasmus' in description:
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
