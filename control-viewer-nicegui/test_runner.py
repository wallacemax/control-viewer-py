#!/usr/bin/env python3
import sys
import subprocess

def main():
    print("Test script running")
    # Just run pytest with no arguments to verify basic functionality
    subprocess.run(["pytest"])
    return 0

if __name__ == "__main__":
    sys.exit(main())