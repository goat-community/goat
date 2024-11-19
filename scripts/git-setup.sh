#!/bin/sh
# If no arguments are given
if [ $# -eq 0 ]; then
  # Display usage and stop
  echo "Usage: git-setup.sh <repo-name::branch::module-name> [<repo-name::branch::module-name> ...]"
  exit 1
fi

# Get remote url to support either https or ssh
remote_url=$(echo $(git config --get remote.origin.url) | sed 's![^/]*$!!')

# Loop through the requested modules
for arg in "$@"; do
  # Split the argument into repo, branch, and module
  repo=$(echo "$arg" | awk -F '::' '{print $1}')
  branch=$(echo "$arg" | awk -F '::' '{print $2}')
  module=$(echo "$arg" | awk -F '::' '{print $3}')

  # Set default values if not provided
  branch=${branch:-main}
  module=${module:-$repo}

  echo "Setting up '$module' module from '$repo' repository on branch '$branch'..."

  # Set the project git URL
  project=$remote_url$repo.git

  # Check if we have access to the module
  if [ "$(git ls-remote "$project" 2>/dev/null)" ]; then
    echo "You have access to '${repo}'"

    # Create the .gitmodules file if it doesn't exist
    ([ -e ".gitmodules" ] || touch ".gitmodules") && [ ! -w ".gitmodules" ] && echo cannot write to .gitmodules && exit 1

    # Prevents duplicate entries
    git config -f .gitmodules --unset-all "submodule.apps/$module.branch"

    # Add the submodule
    git submodule add --force $project "apps/$module"

    # Set the default branch
    git config -f .gitmodules --add "submodule.apps/$module.branch" ${branch}

    # Update to the latest of branch in that submodule
    cd apps/$module && git pull origin ${branch} && cd ../..

    # We forcefully added the submodule which was in .gitignore, so unstage it.
    git restore --staged apps/$module
  else
    echo "You don't have access to: '${repo}' repository."
  fi
done

git restore --staged .gitmodules
