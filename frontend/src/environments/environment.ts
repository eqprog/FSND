export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000/api', // the running FLASK api server url
  auth0: {
    url: 'dev-baow3yyrlofptv6m.us', // the auth0 domain prefix
    audience: 'coffee', // the audience set for the auth0 app
    clientId: 'cbWCx84D9WgjK9ka9EpipGGFGZivcJB2', // the client id generated for the auth0 app
    callbackURL: 'https://127.0.0.1:4200',
  }
};
