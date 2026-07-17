import { Controller, Get, Logger } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { ScraperService } from '../scraper/scraper.service';

@ApiTags('health')
@Controller('health')
export class HealthController {
  private readonly logger = new Logger(HealthController.name);

  constructor(private readonly scraperService: ScraperService) {}

  /**
   * API gateway health check.
   */
  @Get()
  @ApiOperation({ summary: 'Gateway health check' })
  check() {
    return {
      status: 'healthy',
      service: 'api-gateway',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Check whether the scraper microservice is reachable.
   */
  @Get('scraper')
  @ApiOperation({ summary: 'Scraper service health check' })
  async checkScraper() {
    try {
      const scraperHealth = await this.scraperService.checkHealth();
      return {
        gateway: { status: 'healthy' },
        scraper: scraperHealth,
      };
    } catch (error) {
      this.logger.warn('Scraper health check failed');
      return {
        gateway: { status: 'healthy' },
        scraper: {
          status: 'unhealthy',
          error: (error as Error).message,
        },
      };
    }
  }
}
