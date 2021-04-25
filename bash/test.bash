set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="`realpath $DIR/..`"

source "$REPO_DIR/bash/test_python.bash"
source "$REPO_DIR/bash/test_sql.bash"
