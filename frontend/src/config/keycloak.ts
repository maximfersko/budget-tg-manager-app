import Keycloak from 'keycloak-js';

const keycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:9090',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'cash-manager',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'cash-manager-frontend',
};

const keycloak = new Keycloak(keycloakConfig);

export default keycloak;
export { keycloakConfig };

