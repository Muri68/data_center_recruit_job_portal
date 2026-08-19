# core/management/commands/fix_static_issues.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path
import os
import re

class Command(BaseCommand):
    help = 'Fix common static file issues'
    
    def handle(self, *args, **options):
        self.stdout.write('Fixing static file issues...')
        
        # 1. Fix CSS source map references
        static_dir = settings.STATICFILES_DIRS[0]
        css_files = list(static_dir.rglob('*.css'))
        
        fixed_count = 0
        for css_file in css_files:
            try:
                content = css_file.read_text(encoding='utf-8')
                if 'sourceMappingURL' in content:
                    content = re.sub(r'/\*# sourceMappingURL=.*?\*/', '', content)
                    css_file.write_text(content, encoding='utf-8')
                    self.stdout.write(f'Fixed source map: {css_file}')
                    fixed_count += 1
            except Exception as e:
                self.stdout.write(f'Error: {e}')
        
        # 2. Create missing map files
        for css_file in static_dir.rglob('*.min.css'):
            map_file = Path(str(css_file) + '.map')
            if not map_file.exists():
                map_file.touch()
                self.stdout.write(f'Created map file: {map_file}')
        
        # 3. Ensure media directories exist
        media_dirs = ['site', 'blog', 'jobs', 'accounts']
        for media_dir in media_dirs:
            dir_path = settings.MEDIA_ROOT / media_dir
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stdout.write(f'Created media directory: {dir_path}')
        
        # 4. Clear static files
        if settings.STATIC_ROOT.exists():
            import shutil
            shutil.rmtree(settings.STATIC_ROOT)
            self.stdout.write(f'Cleared static root: {settings.STATIC_ROOT}')
        
        # 5. Run collectstatic
        call_command('collectstatic', interactive=False, verbosity=1)
        
        self.stdout.write(self.style.SUCCESS('Static issues fixed successfully!'))