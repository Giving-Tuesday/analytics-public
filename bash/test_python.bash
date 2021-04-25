set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="`realpath $DIR/..`"
SRC_DIR=$REPO_DIR
EXCLUDES=./venv,./.git,conftest.py,setup.py,version.py
CLASSYPY_FILE="$(python -c 'import classypy; print(classypy.__file__)')"
CLASSYPY_DIR="$( cd "$( dirname $CLASSYPY_FILE )" && pwd )"

# Run code for styles
echo "Testing code style..."
flake8 "$SRC_DIR" --exclude "$EXCLUDES"

#echo "Testing Python styles..."
#"$CLASSYPY_DIR/linters/python.sh" "$SRC_DIR" "$EXCLUDES"

#echo "Testing Jupyter Notebook styles..."
#python "$CLASSYPY_DIR/linters/ipynb.py" "$SRC_DIR" --exclude "$EXCLUDES"



echo "Testing code security..."
pushd "$SRC_DIR" > /dev/null
bandit . -ll -r -x "$EXCLUDES"
popd > /dev/null

echo "Testing code complexity..."
xenon "$SRC_DIR" --exclude "${EXCLUDES//.\/},day_of" --ignore "${EXCLUDES//.\/},day_of" --max-average C --max-modules C --max-absolute C

echo "Testing code cruft..."
vulture "$SRC_DIR" "--exclude=${EXCLUDES//.\/}" --sort-by-size | grep -v attribute | grep -v function | grep -v class | echo "$(</dev/stdin)" # function,class imported elsewhere.

python -m pytest --show-capture=no -m 'not xfail' "$REPO_DIR"
