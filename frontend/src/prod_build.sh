#!/bin/bash
if [ $BACKEND_ONLY = "true" ]
then
    yarn install --non-interactive --silent --production
    yarn build
else
    echo "Not placing front end files on the expunger server; this is a dev build."
fi
