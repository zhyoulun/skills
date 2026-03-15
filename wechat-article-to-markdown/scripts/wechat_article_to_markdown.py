import sys
import os

# Add the current directory to sys.path so we can import the module from the source
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "../assets/source"))

from wechat_article_to_markdown import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 wechat_article_to_markdown.py <URL>")
        sys.exit(1)
    
    # Forward arguments to the original main function
    # The original main uses argparse on sys.argv
    main()
