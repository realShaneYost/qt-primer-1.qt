#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from textwrap import dedent


def create_project(dirname, filename):
  project_dir = Path(dirname).expanduser().resolve()
  src_dir = project_dir / "src"
  cmakelists_path = project_dir / "CMakeLists.txt"
  main_cpp_path = src_dir / filename

  project_dir.mkdir(parents=True, exist_ok=False)
  src_dir.mkdir(parents=False, exist_ok=False)

  project_name = project_dir.name

  # Hardcode Qt prefix path for now (specific to my homebrew/macos environment only)
  qt_prefix = "/opt/homebrew/opt/qt"

  cmakelists_template = dedent(f"""\
    cmake_minimum_required(VERSION 3.20)

    project({project_name} LANGUAGES CXX)

    # Use Clang explicitly (on macos this will default to apple clang)
    set(CMAKE_C_COMPILER clang)
    set(CMAKE_CXX_COMPILER clang++)

    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_CXX_EXTENSIONS OFF)

    # Export compile_commands.json for clangd, neovim
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

    # Hardcoded Qt prefix path for now (specific to homebrew/macos environment)
    set(CMAKE_PREFIX_PATH "{qt_prefix}")

    # Enable Qt's automatic processing of MOC/UIC/RCC
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTORCC ON)
    set(CMAKE_AUTOUIC ON)

    # Find Qt6 Core
    find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

    add_executable({project_name}
      src/main.cpp
    )

    target_link_libraries({project_name}
      PRIVATE
        Qt6::Core
        Qt6::Gui
        Qt6::Widgets
    )
  """)

  # Double braces {{ }} escape f-string braces into real C++ braces otherwise it will break
  main_cpp_template = dedent(f"""\
    #include <QCoreApplication>
    #include <QString>
    #include <iostream>
    
    int main(int argc, char** argv)
    {{
      QString msg = QStringLiteral("({project_name}) Basic Linkage Check!");
      std::cout << msg.toStdString() << "\\n";
      return 0;
    }}
  """)

  cmakelists_path.write_text(cmakelists_template, encoding="utf-8")
  main_cpp_path.write_text(main_cpp_template, encoding="utf-8")

  print(f"Created project folder: {project_dir}")
  print(f"Created source folder:  {src_dir}")
  print(f"Created CMakeLists.txt: {cmakelists_path}")
  print(f"Created main.cpp:       {main_cpp_path}")
  print()
  print("To build:")
  print("  cmake -S . -B build")
  print("  cmake --build build")
  print(f"  ./build/{project_name}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="C++/CMake/Clang Qt Project Template Starter")
  parser.add_argument("-d", "--dirname", required=True, help="project directory")
  parser.add_argument("-f", "--filename", default="main.cpp", help="main filename")  
  args = parser.parse_args()

  create_project(args.dirname, args.filename)
  sys.exit(os.EX_OK)
