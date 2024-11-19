#!/bin/sh
# If less than two arguments are given
if [ $# -lt 2 ]; then
  # Display usage and stop
  echo "Usage: git-setup.sh <working-directory> <repo-name::branch::module-name> [<repo-name::branch::module-name> ...]"
  exit 1
fi

# Get the working directory from the first argument
working_directory="$1"
shift

# Check if the working directory exists
if [ ! -d "$working_directory" ]; then
  echo "Working directory '$working_directory' does not exist."
  exit 1
fi

# Change to the working directory
cd "$working_directory" || exit 1

# Get remote URL to support either HTTPS or SSH
remote_url=$(git config --get remote.origin.url | sed 's![^/]*$!!')

# Loop through the requested modules
for arg in "$@"; do
  # Split the argument into repo, branch, and module using 'awk'
  repo=$(echo "$arg" | awk -F'::' '{print $1}')
  branch=$(echo "$arg" | awk -F'::' '{print $2}')
  module=$(echo "$arg" | awk -F'::' '{print $3}')

  # Set default values if not provided
  branch=${branch:-main}
  module=${module:-$repo}

  echo "Setting up '$module' module from '$repo' repository on branch '$branch'..."

  # Set the project git URL
  project="${remote_url}${repo}.git"

  # Check if access to the module is available
  if git ls-remote "$project" &>/dev/null; then
    echo "You have access to '${repo}'"

    # Create the .gitmodules file if it doesn't exist
    [ -e ".gitmodules" ] || touch ".gitmodules"
    [ ! -w ".gitmodules" ] && echo "Cannot write to .gitmodules" && exit 1

    # Prevent duplicate entries
    git config -f .gitmodules --unset-all "submodule.apps/$module.branch" 2>/dev/null

    # Add the submodule
    git submodule add --force "$project" "apps/$module"

    # Set the default branch
    git config -f .gitmodules --add "submodule.apps/$module.branch" "$branch"

    # Update to the latest branch in that submodule
    cd "apps/$module" && git pull origin "$branch" && cd - >/dev/null

    # Unstage the submodule if it was in .gitignore
    git restore --staged "apps/$module"
  else
    echo "You don't have access to '${repo}' repository."
  fi
done

# Unstage .gitmodules if it was in .gitignore
git restore --staged .gitmodules 2>/dev/null
