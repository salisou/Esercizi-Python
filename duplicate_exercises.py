import re

def duplicate_exercises(html_content, section_id, current_count, target=100):
    # Find the section
    section_pattern = rf'(<div id="{section_id}" class="level-section">.*?)(\s*<!-- Pagination for {section_id.capitalize()} -->)'
    section_match = re.search(section_pattern, html_content, re.DOTALL)
    if not section_match:
        return html_content

    section_start = section_match.start()
    section_end = section_match.end()
    section_content = section_match.group(1)
    pagination_part = section_match.group(2)

    # Find all exercises in the section
    exercise_pattern = r'(<!-- Esercizio \d+ -->\s*<div class="exercise">.*?</div>)'
    exercises = re.findall(exercise_pattern, section_content, re.DOTALL)

    if len(exercises) >= target:
        return html_content

    # Duplicate exercises to reach target
    duplicated = ""
    exercise_num = len(exercises) + 1
    while len(exercises) + len(re.findall(r'<!-- Esercizio \d+ -->', duplicated)) < target:
        for exercise in exercises:
            if exercise_num > target:
                break
            # Modify the exercise number and title
            new_exercise = exercise
            # Update the comment
            new_exercise = re.sub(r'Esercizio \d+', f'Esercizio {exercise_num:03d}', new_exercise)
            # Update the number span
            new_exercise = re.sub(r'<span class="exercise-number">Esercizio \d+</span>', f'<span class="exercise-number">Esercizio {exercise_num:03d}</span>', new_exercise)
            # Update the title if it's a variant
            title_match = re.search(r'<span class="exercise-title">([^<]+)</span>', new_exercise)
            if title_match:
                title = title_match.group(1)
                if 'Variante' in title:
                    variant_match = re.search(r'Variante (\d+)', title)
                    if variant_match:
                        variant_num = int(variant_match.group(1)) + 1
                        new_title = re.sub(r'Variante \d+', f'Variante {variant_num}', title)
                    else:
                        new_title = title + ' - Variante 1'
                else:
                    new_title = title + ' - Variante 1'
                new_exercise = re.sub(r'<span class="exercise-title">[^<]+</span>', f'<span class="exercise-title">{new_title}</span>', new_exercise)
            # Update solution id
            new_exercise = re.sub(r'id="solution-\d+"', f'id="solution-{exercise_num}"', new_exercise)
            new_exercise = re.sub(r'toggleSolution\(\d+\)', f'toggleSolution({exercise_num})', new_exercise)
            duplicated += f'\n            <!-- Esercizio {exercise_num:03d} -->\n            {new_exercise}'
            exercise_num += 1
            if exercise_num > target:
                break

    # Insert duplicated exercises before pagination
    new_section_content = section_content + duplicated + pagination_part

    # Replace in html_content
    new_html = html_content[:section_start] + new_section_content + html_content[section_end:]
    return new_html

# Read the file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Duplicate for each section
sections = ['principiante', 'intermedio', 'oop', 'data-analytics']

for section in sections:
    # Count current exercises in the section
    section_pattern = rf'<div id="{section}" class="level-section">(.*?)</div>\s*<!-- Pagination for {section.capitalize()} -->'
    section_match = re.search(section_pattern, content, re.DOTALL)
    if section_match:
        section_content = section_match.group(1)
        current_count = len(re.findall(r'<!-- Esercizio \d+ -->', section_content))
        if current_count < 100:
            content = duplicate_exercises(content, section, current_count, 100)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Duplication completed.")
