from psu_report_generator import main, generate_html_report

# 生成 4/1 報告
html_content, filepath = main('20260401')
print(f"報告已生成: {filepath}")
