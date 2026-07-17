/** Default configuration for the scraper microservice connection. */
export const SCRAPER_CONFIG = {
  baseUrl: process.env.SCRAPER_SERVICE_URL ?? 'http://localhost:3011',
  timeout: 30_000,
  retryAttempts: 2,
} as const;
