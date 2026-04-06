const { execSync } = require('child_process');
const fs = require('fs');

try {
    console.log('Executing Python script...');
    const result = execSync('python.exe "D:/claude mini max 2.7/.claude/CoBM_BQT_Analysis.py" 2> "D:/claude mini max 2.7/.claude/error.txt"', {
        encoding: 'utf8',
        cwd: 'D:/claude mini max 2.7/.claude',
        timeout: 60000
    });
    console.log('Result:', result);
} catch (error) {
    console.error('Error:', error.message);
}

try {
    const errorContent = fs.readFileSync('D:/claude mini max 2.7/.claude/error.txt', 'utf8');
    console.log('Error file content:', errorContent);
} catch (e) {
    console.log('No error file found');
}
