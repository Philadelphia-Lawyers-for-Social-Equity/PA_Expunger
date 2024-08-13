#!/bin/bash

HOOK_PATH="./.git/hooks"
echo "setting up git hooks"
mkdir $HOOK_PATH
cp ./init/post-commit.sh $HOOK_PATH/post-commit
cp ./init/pre-commit.sh $HOOK_PATH/pre-commit
chmod u+x $HOOK_PATH/post-commit &&
chmod u+x $HOOK_PATH/pre-commit &&
echo "setup complete"