let config = {};

// config.json is written into STATIC_ROOT at container start and served under
// STATIC_URL, which is also what Vite's base compiles to here. See Dockerfile.prod.
// BASE_URL is Vite's resolved config.base, baked in at build time; see vite.config.js.
const configReady = fetch(`${import.meta.env.BASE_URL}config.json`)
    .then((res) => (res.ok ? res.json() : {}))
    .then((data) => { config = data; })
    .catch(() => {});

export const getAppConfig = () => config;
export const appConfigReady = configReady;
