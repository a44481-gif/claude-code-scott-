const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// 163.com SMTP configuration
const config = {
    host: 'smtp.163.com',
    port: 465,
    secure: true,
    auth: {
        user: 'h13751019800@163.com',
        pass: 'FZQAXDZUHDWQHUIO'
    }
};

async function sendEmail() {
    console.log('Creating transporter...');
    const transporter = nodemailer.createTransport(config);
    
    // Read HTML report
    const htmlPath = path.join(__dirname, 'psu_daily_report_20260402.html');
    console.log('Reading HTML report from:', htmlPath);
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');

    const mailOptions = {
        from: '"PSU Sales Report" <h13751019800@163.com>',
        to: 'h13751019800@163.com',
        subject: 'Daily PSU Sales Report - 2026-04-02 (16 Brands)',
        html: htmlContent
    };
    
    console.log('Sending email...');
    try {
        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent successfully!');
        console.log('Message ID:', info.messageId);
        return true;
    } catch (error) {
        console.error('Error sending email:', error);
        return false;
    }
}

sendEmail().then(success => {
    console.log(success ? 'DONE' : 'FAILED');
    process.exit(success ? 0 : 1);
});