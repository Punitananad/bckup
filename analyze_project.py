"""
Django Project Analyzer - scan2food
Generates comprehensive technical documentation for project deployment
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

class DjangoProjectAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.django_root = self.project_root / "application" / "scan2food"
        self.report = {
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_structure": {},
            "django_apps": [],
            "settings_analysis": {},
            "database_config": {},
            "environment_variables": [],
            "dependencies": [],
            "urls_mapping": {},
            "models_summary": {},
            "static_media_config": {},
            "websocket_config": {},
            "deployment_checklist": []
        }
    
    def analyze_project_structure(self):
        """Analyze the overall project structure"""
        print("📁 Analyzing project structure...")
        
        structure = {
            "main_django_app": str(self.django_root),
            "apps_found": [],
            "key_directories": {}
        }
        
        # Find all Django apps
        if self.django_root.exists():
            for item in self.django_root.iterdir():
                if item.is_dir() and (item / "apps.py").exists():
                    structure["apps_found"].append(item.name)
        
        # Key directories
        key_dirs = ["media", "static_files", "templates", "migrations", "backup_script"]
        for dir_name in key_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path = self.django_root / dir_name
            if dir_path.exists():
                structure["key_directories"][dir_name] = str(dir_path)
        
        self.report["project_structure"] = structure
        return structure
    
    def analyze_settings(self):
        """Analyze Django settings.py"""
        print("⚙️  Analyzing Django settings...")
        
        settings_file = self.django_root / "theatreApp" / "settings.py"
        if not settings_file.exists():
            return {"error": "settings.py not found"}
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        settings = {
            "file_location": str(settings_file),
            "debug_mode": self._extract_setting(content, "DEBUG"),
            "allowed_hosts": self._extract_setting(content, "ALLOWED_HOSTS"),
            "installed_apps": self._extract_list_setting(content, "INSTALLED_APPS"),
            "middleware": self._extract_list_setting(content, "MIDDLEWARE"),
            "templates_config": "TEMPLATES" in content,
            "static_url": self._extract_setting(content, "STATIC_URL"),
            "static_root": self._extract_setting(content, "STATIC_ROOT"),
            "media_url": self._extract_setting(content, "MEDIA_URL"),
            "media_root": self._extract_setting(content, "MEDIA_ROOT"),
            "wsgi_application": self._extract_setting(content, "WSGI_APPLICATION"),
            "asgi_application": self._extract_setting(content, "ASGI_APPLICATION"),
        }
        
        self.report["settings_analysis"] = settings
        return settings
    
    def analyze_database(self):
        """Analyze database configuration"""
        print("🗄️  Analyzing database configuration...")
        
        settings_file = self.django_root / "theatreApp" / "settings.py"
        if not settings_file.exists():
            return {"error": "settings.py not found"}
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        db_config = {
            "database_section_found": "DATABASES" in content,
            "sqlite_db_file": None,
            "mysql_config": False,
            "postgresql_config": False
        }
        
        # Check for SQLite
        if "db.sqlite3" in content:
            db_config["sqlite_db_file"] = "db.sqlite3"
            db_file = self.django_root / "db.sqlite3"
            db_config["sqlite_exists"] = db_file.exists()
            if db_file.exists():
                db_config["sqlite_size_mb"] = round(db_file.stat().st_size / (1024*1024), 2)
        
        # Check for MySQL/PostgreSQL
        if "mysql" in content.lower():
            db_config["mysql_config"] = True
        if "postgresql" in content.lower() or "psycopg" in content.lower():
            db_config["postgresql_config"] = True
        
        self.report["database_config"] = db_config
        return db_config
    
    def find_environment_variables(self):
        """Find all environment variables used"""
        print("🔐 Finding environment variables...")
        
        env_vars = set()
        patterns = [
            r'os\.environ\.get\([\'"]([^\'"]+)[\'"]',
            r'os\.getenv\([\'"]([^\'"]+)[\'"]',
            r'env\([\'"]([^\'"]+)[\'"]'
        ]
        
        # Search in settings.py
        settings_file = self.django_root / "theatreApp" / "settings.py"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    env_vars.update(matches)
        
        # Check for .env file
        env_file_locations = []
        for env_name in [".env", ".env.example", ".env.local"]:
            env_path = self.django_root / env_name
            if env_path.exists():
                env_file_locations.append(str(env_path))
        
        self.report["environment_variables"] = {
            "variables_found": sorted(list(env_vars)),
            "env_files": env_file_locations,
            "total_count": len(env_vars)
        }
        return self.report["environment_variables"]
    
    def analyze_dependencies(self):
        """Analyze project dependencies"""
        print("📦 Analyzing dependencies...")
        
        req_files = ["requirements.txt", "requirement.txt"]
        dependencies = []
        
        for req_file in req_files:
            req_path = self.django_root / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        dependencies.extend(deps)
                except UnicodeDecodeError:
                    try:
                        with open(req_path, 'r', encoding='latin-1') as f:
                            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                            dependencies.extend(deps)
                    except:
                        print(f"⚠️  Could not read {req_file}")
        
        self.report["dependencies"] = {
            "total_packages": len(dependencies),
            "packages": dependencies,
            "key_packages": self._identify_key_packages(dependencies)
        }
        return self.report["dependencies"]
    
    def analyze_apps(self):
        """Analyze each Django app"""
        print("🎯 Analyzing Django apps...")
        
        apps = []
        app_dirs = ["adminPortal", "theatre", "chat_bot", "chat_box", "website"]
        
        for app_name in app_dirs:
            app_path = self.django_root / app_name
            if app_path.exists():
                app_info = {
                    "name": app_name,
                    "path": str(app_path),
                    "has_models": (app_path / "models.py").exists(),
                    "has_views": (app_path / "views.py").exists(),
                    "has_urls": (app_path / "urls.py").exists(),
                    "has_admin": (app_path / "admin.py").exists(),
                    "has_api_views": (app_path / "api_views.py").exists(),
                    "has_forms": (app_path / "form.py").exists() or (app_path / "forms.py").exists(),
                    "has_templates": (app_path / "templates").exists(),
                    "has_migrations": (app_path / "migrations").exists(),
                    "has_consumers": (app_path / "consumers").exists() or (app_path / "consumer").exists(),
                    "has_routing": (app_path / "routing.py").exists(),
                }
                
                # Count models
                if app_info["has_models"]:
                    app_info["models_count"] = self._count_models(app_path / "models.py")
                
                apps.append(app_info)
        
        self.report["django_apps"] = apps
        return apps
    
    def analyze_urls(self):
        """Analyze URL routing"""
        print("🔗 Analyzing URL routing...")
        
        main_urls = self.django_root / "theatreApp" / "urls.py"
        url_patterns = {}
        
        if main_urls.exists():
            with open(main_urls, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find include patterns
                includes = re.findall(r'path\([\'"]([^\'"]*)[\'"],\s*include\([\'"]([^\'"]+)[\'"]', content)
                for pattern, include_path in includes:
                    url_patterns[pattern] = include_path
        
        self.report["urls_mapping"] = url_patterns
        return url_patterns
    
    def analyze_websocket_config(self):
        """Analyze WebSocket/ASGI configuration"""
        print("🔌 Analyzing WebSocket configuration...")
        
        asgi_file = self.django_root / "theatreApp" / "asgi.py"
        ws_config = {
            "asgi_configured": asgi_file.exists(),
            "channels_installed": False,
            "routing_files": []
        }
        
        # Check for channels in dependencies
        if "channels" in str(self.report.get("dependencies", {})):
            ws_config["channels_installed"] = True
        
        # Find routing files
        for app_name in ["theatre", "chat_bot", "chat_box"]:
            routing_file = self.django_root / app_name / "routing.py"
            if routing_file.exists():
                ws_config["routing_files"].append(str(routing_file))
        
        self.report["websocket_config"] = ws_config
        return ws_config
    
    def analyze_static_media(self):
        """Analyze static and media files configuration"""
        print("📸 Analyzing static and media files...")
        
        config = {
            "media_dir": str(self.django_root / "media"),
            "media_exists": (self.django_root / "media").exists(),
            "static_files_dir": str(self.project_root / "static_files"),
            "static_exists": (self.project_root / "static_files").exists(),
        }
        
        # Count media files
        media_path = self.django_root / "media"
        if media_path.exists():
            config["media_subdirs"] = [d.name for d in media_path.iterdir() if d.is_dir()]
        
        self.report["static_media_config"] = config
        return config
    
    def generate_deployment_checklist(self):
        """Generate deployment checklist"""
        print("✅ Generating deployment checklist...")
        
        checklist = [
            {
                "task": "Update settings.py for production",
                "items": [
                    "Set DEBUG = False",
                    "Update ALLOWED_HOSTS with new IP/domain",
                    "Configure SECRET_KEY from environment variable",
                    "Update CSRF_TRUSTED_ORIGINS if needed"
                ]
            },
            {
                "task": "Database setup",
                "items": [
                    "Create database (if using MySQL/PostgreSQL)",
                    "Update database credentials in settings or .env",
                    "Run: python manage.py migrate",
                    "Create superuser: python manage.py createsuperuser"
                ]
            },
            {
                "task": "Static files",
                "items": [
                    "Run: python manage.py collectstatic",
                    "Configure web server to serve static files",
                    "Configure web server to serve media files"
                ]
            },
            {
                "task": "Environment variables",
                "items": [
                    "Create .env file with all required variables",
                    f"Required variables: {', '.join(self.report['environment_variables'].get('variables_found', [])[:5])}"
                ]
            },
            {
                "task": "Dependencies",
                "items": [
                    "Install Python packages: pip install -r requirements.txt",
                    "Install system dependencies (if any)",
                    "Install Redis (if using Channels/WebSockets)"
                ]
            },
            {
                "task": "WebSocket/ASGI setup (if applicable)",
                "items": [
                    "Install and configure Daphne or Uvicorn",
                    "Configure Redis for channel layers",
                    "Update ASGI application settings"
                ]
            },
            {
                "task": "Web server configuration",
                "items": [
                    "Configure Nginx/Apache",
                    "Set up reverse proxy to Django",
                    "Configure SSL certificate",
                    "Set up firewall rules"
                ]
            },
            {
                "task": "Security",
                "items": [
                    "Update SECRET_KEY",
                    "Configure SECURE_SSL_REDIRECT if using HTTPS",
                    "Set SECURE_HSTS_SECONDS",
                    "Configure SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE"
                ]
            }
        ]
        
        self.report["deployment_checklist"] = checklist
        return checklist
    
    def _extract_setting(self, content, setting_name):
        """Extract a setting value from settings.py"""
        pattern = f'{setting_name}\\s*=\\s*(.+?)(?:\\n|$)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_list_setting(self, content, setting_name):
        """Extract a list setting from settings.py"""
        pattern = f'{setting_name}\\s*=\\s*\\[(.*?)\\]'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            items = re.findall(r'[\'"]([^\'"]+)[\'"]', match.group(1))
            return items
        return []
    
    def _count_models(self, models_file):
        """Count Django models in a file"""
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count class definitions that inherit from models.Model
                matches = re.findall(r'class\s+\w+\([^)]*models\.Model[^)]*\)', content)
                return len(matches)
        except:
            return 0
    
    def _identify_key_packages(self, dependencies):
        """Identify key packages from dependencies"""
        key_packages = {}
        important = ['django', 'channels', 'daphne', 'redis', 'celery', 'gunicorn', 
                     'mysql', 'psycopg', 'pillow', 'rest_framework']
        
        for dep in dependencies:
            dep_lower = dep.lower()
            for key in important:
                if key in dep_lower:
                    key_packages[key] = dep
        
        return key_packages
    
    def run_full_analysis(self):
        """Run complete project analysis"""
        print("🚀 Starting Django Project Analysis...\n")
        
        self.analyze_project_structure()
        self.analyze_settings()
        self.analyze_database()
        self.find_environment_variables()
        self.analyze_dependencies()
        self.analyze_apps()
        self.analyze_urls()
        self.analyze_websocket_config()
        self.analyze_static_media()
        self.generate_deployment_checklist()
        
        print("\n✨ Analysis complete!")
        return self.report
    
    def save_report(self, output_file="project_explain.json"):
        """Save report to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Report saved to: {output_file}")
    
    def generate_markdown_report(self, output_file="project_explain.md"):
        """Generate human-readable markdown report"""
        md_content = f"""# Django Project Analysis Report - scan2food
**Generated:** {self.report['analysis_date']}

---

## 📋 Project Overview

### Project Structure
- **Main Django App Location:** `{self.report['project_structure'].get('main_django_app', 'N/A')}`
- **Django Apps Found:** {len(self.report['django_apps'])}

### Applications
"""
        
        for app in self.report['django_apps']:
            md_content += f"\n#### {app['name']}\n"
            md_content += f"- **Path:** `{app['path']}`\n"
            md_content += f"- **Has Models:** {'✅' if app['has_models'] else '❌'}"
            if app.get('models_count'):
                md_content += f" ({app['models_count']} models)"
            md_content += "\n"
            md_content += f"- **Has Views:** {'✅' if app['has_views'] else '❌'}\n"
            md_content += f"- **Has URLs:** {'✅' if app['has_urls'] else '❌'}\n"
            md_content += f"- **Has API Views:** {'✅' if app['has_api_views'] else '❌'}\n"
            md_content += f"- **Has Templates:** {'✅' if app['has_templates'] else '❌'}\n"
            md_content += f"- **WebSocket Support:** {'✅' if app['has_consumers'] or app['has_routing'] else '❌'}\n"
        
        md_content += f"""

---

## ⚙️ Django Settings

### Configuration File
- **Location:** `{self.report['settings_analysis'].get('file_location', 'N/A')}`

### Key Settings
- **DEBUG Mode:** `{self.report['settings_analysis'].get('debug_mode', 'N/A')}`
- **ALLOWED_HOSTS:** `{self.report['settings_analysis'].get('allowed_hosts', 'N/A')}`
- **WSGI Application:** `{self.report['settings_analysis'].get('wsgi_application', 'N/A')}`
- **ASGI Application:** `{self.report['settings_analysis'].get('asgi_application', 'N/A')}`

### Static & Media Files
- **STATIC_URL:** `{self.report['settings_analysis'].get('static_url', 'N/A')}`
- **STATIC_ROOT:** `{self.report['settings_analysis'].get('static_root', 'N/A')}`
- **MEDIA_URL:** `{self.report['settings_analysis'].get('media_url', 'N/A')}`
- **MEDIA_ROOT:** `{self.report['settings_analysis'].get('media_root', 'N/A')}`

### Installed Apps
"""
        
        for app in self.report['settings_analysis'].get('installed_apps', []):
            md_content += f"- {app}\n"
        
        md_content += f"""

---

## 🗄️ Database Configuration

- **SQLite Database:** `{self.report['database_config'].get('sqlite_db_file', 'Not configured')}`
- **SQLite Exists:** {'✅' if self.report['database_config'].get('sqlite_exists') else '❌'}
"""
        
        if self.report['database_config'].get('sqlite_size_mb'):
            md_content += f"- **Database Size:** {self.report['database_config']['sqlite_size_mb']} MB\n"
        
        md_content += f"- **MySQL Configured:** {'✅' if self.report['database_config'].get('mysql_config') else '❌'}\n"
        md_content += f"- **PostgreSQL Configured:** {'✅' if self.report['database_config'].get('postgresql_config') else '❌'}\n"
        
        md_content += f"""

---

## 🔐 Environment Variables

### Required Variables ({self.report['environment_variables'].get('total_count', 0)} found)
"""
        
        for var in self.report['environment_variables'].get('variables_found', []):
            md_content += f"- `{var}`\n"
        
        md_content += "\n### .env File Locations\n"
        env_files = self.report['environment_variables'].get('env_files', [])
        if env_files:
            for env_file in env_files:
                md_content += f"- `{env_file}`\n"
        else:
            md_content += "- ⚠️ No .env file found - you need to create one!\n"
        
        md_content += f"""

---

## 📦 Dependencies

**Total Packages:** {self.report['dependencies'].get('total_packages', 0)}

### Key Packages
"""
        
        for key, package in self.report['dependencies'].get('key_packages', {}).items():
            md_content += f"- **{key}:** `{package}`\n"
        
        md_content += "\n### All Dependencies\n```\n"
        for dep in self.report['dependencies'].get('packages', []):
            md_content += f"{dep}\n"
        md_content += "```\n"
        
        md_content += f"""

---

## 🔗 URL Routing

### Main URL Patterns
"""
        
        for pattern, include_path in self.report['urls_mapping'].items():
            md_content += f"- `/{pattern}` → `{include_path}`\n"
        
        md_content += f"""

---

## 🔌 WebSocket Configuration

- **ASGI Configured:** {'✅' if self.report['websocket_config'].get('asgi_configured') else '❌'}
- **Channels Installed:** {'✅' if self.report['websocket_config'].get('channels_installed') else '❌'}

### Routing Files
"""
        
        for routing_file in self.report['websocket_config'].get('routing_files', []):
            md_content += f"- `{routing_file}`\n"
        
        md_content += f"""

---

## 📸 Static & Media Files

- **Media Directory:** `{self.report['static_media_config'].get('media_dir', 'N/A')}`
- **Media Exists:** {'✅' if self.report['static_media_config'].get('media_exists') else '❌'}
- **Static Files Directory:** `{self.report['static_media_config'].get('static_files_dir', 'N/A')}`
- **Static Exists:** {'✅' if self.report['static_media_config'].get('static_exists') else '❌'}

### Media Subdirectories
"""
        
        for subdir in self.report['static_media_config'].get('media_subdirs', []):
            md_content += f"- {subdir}\n"
        
        md_content += "\n---\n\n## ✅ Deployment Checklist\n\n"
        
        for section in self.report['deployment_checklist']:
            md_content += f"### {section['task']}\n\n"
            for item in section['items']:
                md_content += f"- [ ] {item}\n"
            md_content += "\n"
        
        md_content += """

---

## 🚀 Quick Deployment Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 4. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 5. Run with Daphne (for WebSockets)
```bash
daphne -b 0.0.0.0 -p 8000 theatreApp.asgi:application
```

---

## 📝 Important Notes

1. **Environment Variables:** Create a `.env` file in the Django root directory with all required variables
2. **Database:** Ensure database is properly configured before running migrations
3. **Static Files:** Configure your web server (Nginx/Apache) to serve static and media files
4. **WebSockets:** If using WebSockets, ensure Redis is installed and configured
5. **Security:** Update SECRET_KEY, set DEBUG=False, and configure ALLOWED_HOSTS for production

---

*Report generated by Django Project Analyzer*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📄 Markdown report saved to: {output_file}")


if __name__ == "__main__":
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Create analyzer instance
    analyzer = DjangoProjectAnalyzer(project_root)
    
    # Run full analysis
    report = analyzer.run_full_analysis()
    
    # Save reports
    analyzer.save_report("project_explain.json")
    analyzer.generate_markdown_report("project_explain.md")
    
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    print(f"✅ Django Apps Found: {len(report['django_apps'])}")
    print(f"✅ Dependencies: {report['dependencies']['total_packages']} packages")
    print(f"✅ Environment Variables: {report['environment_variables']['total_count']} variables")
    print(f"✅ URL Patterns: {len(report['urls_mapping'])} patterns")
    print(f"✅ WebSocket Configured: {'Yes' if report['websocket_config']['asgi_configured'] else 'No'}")
    print("="*60)
    print("\n📁 Output files created:")
    print("   - project_explain.json (detailed JSON report)")
    print("   - project_explain.md (human-readable documentation)")
    print("\n🎉 Done! Check the generated files for complete project documentation.")
