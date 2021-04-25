set -e  # Stop on first failure.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="`realpath $DIR/..`"
EXCLUDES=$REPO_DIR/day_of/*,$REPO_DIR/fep/*,$REPO_DIR/fep-2021/*,$REPO_DIR/version.py,$REPO_DIR/external/*,$REPO_DIR/airflow/dags/sql/fep/data/raw/*
SQL_LINTING_PATH="${*:-$REPO_DIR}"
CLASSYPY_FILE="$(python -c 'import classypy; print(classypy.__file__)')"
CLASSYPY_DIR="$( cd "$( dirname $CLASSYPY_FILE )" && pwd )"

echo "Testing Data Insights annotations..."
"$CLASSYPY_DIR/linters/annotations.sh" "$REPO_DIR" "$EXCLUDES"

echo "Testing sql style..."
python "$CLASSYPY_DIR/linters/sql.py" "$SQL_LINTING_PATH" --fix --exclude "$EXCLUDES"
