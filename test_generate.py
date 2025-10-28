from PIL import Image
import os
from report_generator_system import generate_report_pdf

os.makedirs('uploads', exist_ok=True)
# create 4 small test images
paths = []
for i in range(4):
    p = os.path.join('uploads', f'test_img_{i}.png')
    img = Image.new('RGB', (200, 100), color=(255, 200, 200))
    img.save(p)
    paths.append(p)

out = generate_report_pdf(
    activity_name='تجربة',
    execution_date='1447-09-14',
    executor_name='وليد',
    place='جدة',
    target_group='طلاب',
    evidence_paths=paths
)

print('Generated:', out)
print('Exists:', os.path.exists(out))
