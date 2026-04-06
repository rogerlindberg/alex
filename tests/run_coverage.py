import os
import subprocess


def run_coverage():
    run_coverage_with_tests()
    create_html_report()
    open_html_page()


def run_coverage_with_tests():
    cmd = ["coverage", "run", "-m", "pytest"]
    subprocess.check_call(cmd)


def create_html_report():
    cmd = ["coverage", "html"]
    subprocess.check_call(cmd)


def open_html_page():
    print(os.getcwd())
    os.system("start htmlcov/index.html")


if __name__ == "__main__":
    run_coverage()
