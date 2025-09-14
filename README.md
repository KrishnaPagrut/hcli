# hcli
HumanCLI
 python file_diff.py test_output_strict.txt test_output_user.txt

Single File
 python3 ast_chunker.py filename.py 
 python3 pyh_ast_generator.py filename.ast.json path_to_py_file
 python3 pyh_ast_to_output.py filename.pyh.ast.json
 python3 crawl_repo.py repo_to_crawl -o out
 python3 diff_analyzer.py filename.pyh.json test_strict_op.txt test_user_op.txt -o changes.json
 python3 apply_changes_demo.py filename.py


Need to figure out 
 The pyh json keeps putting '''json''' at the beginning and end of the file.
 How is the UI going to handle 
