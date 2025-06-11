import { execSync } from 'child_process';

try {
  console.log('Initializing git submodules...');
  execSync('git submodule update --init --recursive', { stdio: 'inherit' });
  console.log('Git submodules initialized successfully');
} catch (error) {
  console.error('Error: Failed to initialize git submodules');
  process.exit(1);
} 