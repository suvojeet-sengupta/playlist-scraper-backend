export default () => ({
  port: parseInt(process.env.PORT ?? '3010', 10),
  scraperServiceUrl:
    process.env.SCRAPER_SERVICE_URL ?? 'http://localhost:3011',
  nodeEnv: process.env.NODE_ENV ?? 'development',
});
