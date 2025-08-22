from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = collect_data_files("pymeshlab")
binaries = collect_dynamic_libs("pymeshlab")