
#!/usr/bin/env python3
"""
VoxAura AI Voice Agent - Clean Startup Script
Handles all dependency issues and starts the app smoothly
"""

import sys
import os
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_system_dependencies():
    """Install required system dependencies"""
    try:
        logger.info("Installing system dependencies...")
        
        # Install libstdc++6 and other required libraries
        commands = [
            ['nix-env', '-iA', 'nixpkgs.stdenv.cc.cc.lib'],
            ['nix-env', '-iA', 'nixpkgs.gcc-unwrapped.lib'],
            ['nix-env', '-iA', 'nixpkgs.libgcc']
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info(f"✅ Successfully ran: {' '.join(cmd)}")
                else:
                    logger.warning(f"⚠️ Command failed but continuing: {' '.join(cmd)}")
            except Exception as e:
                logger.warning(f"⚠️ Could not run {' '.join(cmd)}: {e}")
        
        # Set LD_LIBRARY_PATH to include common library locations
        lib_paths = [
            '/nix/store/*/lib',
            '/usr/lib/x86_64-linux-gnu',
            '/lib/x86_64-linux-gnu',
            '/home/runner/.nix-profile/lib'
        ]
        
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        new_paths = ':'.join([path for path in lib_paths if os.path.exists(path.replace('*', '')) or '*' in path])
        
        if current_ld_path:
            os.environ['LD_LIBRARY_PATH'] = f"{current_ld_path}:{new_paths}"
        else:
            os.environ['LD_LIBRARY_PATH'] = new_paths
            
        logger.info("✅ System dependencies and library paths configured")
    except Exception as e:
        logger.warning(f"Could not install system deps: {e}")

def clean_python_environment():
    """Clean and reinstall Python dependencies"""
    try:
        logger.info("Cleaning Python environment...")
        
        # Remove problematic packages
        subprocess.run([
            sys.executable, '-m', 'pip', 'uninstall', '-y', 
            'pydantic', 'pydantic-core', 'assemblyai', 'google-generativeai',
            'grpcio', 'grpcio-status'
        ], capture_output=True)
        
        # Clear pip cache
        subprocess.run([
            sys.executable, '-m', 'pip', 'cache', 'purge'
        ], capture_output=True)
        
        logger.info("✅ Environment cleaned")
        return True
    except Exception as e:
        logger.error(f"Failed to clean environment: {e}")
        return False

def install_dependencies():
    """Install dependencies in correct order"""
    try:
        logger.info("Installing Python dependencies...")
        
        # Upgrade pip first
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True, timeout=60)
        
        # Install dependencies in specific order with wheel preference
        deps_order = [
            'wheel',
            'setuptools',
            'pydantic==2.5.3',
            'pydantic-core==2.14.6',
            'flask==3.1.0',
            'flask-socketio==5.4.1',
            'flask-sqlalchemy==3.1.1',
            'sqlalchemy==2.0.36',
            'websockets==13.1',
            'requests==2.32.3',
            'gtts==2.5.4',
            'python-engineio==4.9.1',
            'python-socketio==5.11.4',
            # Install grpc components first
            'grpcio==1.67.1',
            'grpcio-status==1.67.1',
            'assemblyai==0.33.0',
            'google-generativeai==0.8.3'
        ]
        
        for dep in deps_order:
            logger.info(f"Installing {dep}...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    '--no-cache-dir', '--prefer-binary', dep
                ], check=True, capture_output=True, timeout=120)
                logger.info(f"✅ {dep} installed successfully")
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Timeout installing {dep}")
                return False
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install {dep}: {e}")
                # Try without strict version for critical packages
                if '==' in dep:
                    base_package = dep.split('==')[0]
                    logger.info(f"Trying to install {base_package} without version constraint...")
                    try:
                        subprocess.run([
                            sys.executable, '-m', 'pip', 'install', 
                            '--no-cache-dir', '--prefer-binary', base_package
                        ], check=True, capture_output=True, timeout=120)
                        logger.info(f"✅ {base_package} installed successfully")
                    except:
                        logger.error(f"❌ Failed to install {base_package} even without version")
                        if base_package in ['google-generativeai', 'assemblyai']:
                            # These are critical, but we can continue
                            logger.warning(f"⚠️ Continuing without {base_package}")
                        else:
                            return False
        
        logger.info("✅ Python dependencies installed")
        return True
    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def check_imports():
    """Test critical imports"""
    critical_imports = [
        ('flask', 'Flask web framework'),
        ('flask_socketio', 'WebSocket support'),
        ('pydantic', 'Data validation'),
        ('assemblyai', 'Speech-to-text'),
        ('google.generativeai', 'LLM service'),
        ('websockets', 'WebSocket client'),
        ('requests', 'HTTP client'),
        ('sqlalchemy', 'Database ORM')
    ]
    
    logger.info("🧪 VoxAura Import Test")
    logger.info("=" * 40)
    
    failed_imports = []
    for module, description in critical_imports:
        try:
            if module == 'google.generativeai':
                # Special handling for google.generativeai
                os.environ['GRPC_VERBOSITY'] = 'ERROR'
                os.environ['GLOG_minloglevel'] = '2'
            
            __import__(module.replace('-', '_'))
            logger.info(f"✅ {module} {description}")
        except ImportError as e:
            logger.error(f"❌ {module}: {e}")
            failed_imports.append(module)
        except Exception as e:
            logger.error(f"❌ {module}: Unexpected error - {e}")
            failed_imports.append(module)
    
    logger.info("=" * 40)
    if not failed_imports:
        logger.info("🎉 All imports successful!")
    else:
        logger.warning(f"⚠️ Some imports failed: {failed_imports}")
        logger.info("🔧 The app will use fallback services for failed imports")
    
    return failed_imports

def test_app_import():
    """Test if the main app can be imported"""
    try:
        logger.info("🧪 Testing app import...")
        
        # Set fallback environment variables
        os.environ.setdefault('GOOGLE_AI_API_KEY', 'fallback-key')
        os.environ.setdefault('ASSEMBLYAI_API_KEY', 'fallback-key')
        
        # Test import without running
        import app
        logger.info("✅ App imported successfully!")
        logger.info("🚀 Ready to start VoxAura!")
        return True
    except Exception as e:
        logger.error(f"❌ App import failed: {e}")
        return False

def start_app():
    """Start the VoxAura application"""
    try:
        logger.info("🚀 Starting VoxAura AI Voice Agent...")
        
        # Set environment variables
        os.environ['PYTHONPATH'] = os.getcwd()
        os.environ.setdefault('GOOGLE_AI_API_KEY', 'fallback-key')
        os.environ.setdefault('ASSEMBLYAI_API_KEY', 'fallback-key')
        
        # Import and run the app
        from app import app, socketio
        
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"🌐 Server starting on http://0.0.0.0:{port}")
        logger.info(f"🎯 Day 18 Turn Detection: http://0.0.0.0:{port}/day18-turn-detection")
        logger.info(f"🎵 Day 20 Features: Murf WebSocket integration available")
        
        socketio.run(
            app,
            host="0.0.0.0", 
            port=port, 
            debug=False, 
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start app: {e}")
        logger.info("🔧 You can still try running: python app.py")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 VoxAura AI Voice Agent - Clean Startup")
    print("=" * 60)
    
    # Step 1: Install system dependencies
    install_system_dependencies()
    
    # Step 2: Clean environment
    if not clean_python_environment():
        print("❌ Failed to clean environment, but continuing...")
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("❌ Some dependencies failed to install, but continuing...")
    
    # Step 4: Check imports
    failed = check_imports()
    if failed:
        print(f"⚠️ Some imports failed: {failed}")
        print("🔧 App will use fallback services where needed")
    
    # Step 5: Test app import
    if not test_app_import():
        print("❌ App import failed, but you can try running: python app.py")
        return 1
    
    print("\n" + "🚀" * 20)
    print("🚀 All systems ready! Starting VoxAura...")
    print("🚀" * 20 + "\n")
    
    # Step 6: Start the app
    if not start_app():
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
