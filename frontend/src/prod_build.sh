if [ $BACKEND_ONLY = "true" ]
then
    RUN yarn install --non-interactive --silent --production
    RUN yarn build
else
    echo "Not placing front end files on the expunger server; this is a dev build."
fi
