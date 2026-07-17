import {
  Injectable,
  Logger,
  ServiceUnavailableException,
  GatewayTimeoutException,
  HttpException,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';
import {
  IPlaylistResponse,
  IPlatformsResponse,
} from '../../common/interfaces/playlist.interface';

@Injectable()
export class ScraperService {
  private readonly logger = new Logger(ScraperService.name);
  private readonly baseUrl: string;

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.baseUrl =
      this.configService.get<string>('scraperServiceUrl') ??
      'http://localhost:3011';
    this.logger.log(`Scraper service URL: ${this.baseUrl}`);
  }

  /**
   * Send a playlist URL to the scraper service and return structured data.
   */
  async scrapePlaylist(url: string): Promise<IPlaylistResponse> {
    this.logger.log(`Scraping playlist: ${url}`);
    try {
      const response = await firstValueFrom(
        this.httpService.post<IPlaylistResponse>(
          `${this.baseUrl}/api/scrape`,
          { url },
          { timeout: 30_000 },
        ),
      );
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError, 'scrapePlaylist');
    }
  }

  /**
   * Retrieve the list of supported platforms from the scraper service.
   */
  async getSupportedPlatforms(): Promise<IPlatformsResponse> {
    try {
      const response = await firstValueFrom(
        this.httpService.get<IPlatformsResponse>(
          `${this.baseUrl}/api/platforms`,
          { timeout: 10_000 },
        ),
      );
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError, 'getSupportedPlatforms');
    }
  }

  /**
   * Check the health of the scraper service.
   */
  async checkHealth(): Promise<Record<string, unknown>> {
    try {
      const response = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/api/health`, { timeout: 5_000 }),
      );
      return response.data as Record<string, unknown>;
    } catch (error) {
      this.handleError(error as AxiosError, 'checkHealth');
    }
  }

  /**
   * Map Axios errors to appropriate NestJS HTTP exceptions.
   */
  private handleError(error: AxiosError, context: string): never {
    this.logger.error(
      `Scraper service error [${context}]: ${error.message}`,
    );

    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      throw new ServiceUnavailableException(
        'Scraper service is unavailable. Please try again later.',
      );
    }

    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
      throw new GatewayTimeoutException(
        'Scraper service did not respond in time. The playlist may be very large.',
      );
    }

    // Forward HTTP errors from the scraper service
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as Record<string, unknown> | undefined;
      const detail = data?.['detail'] ?? data?.['error'] ?? error.message;
      throw new HttpException(
        typeof detail === 'object' ? detail : { message: detail },
        status,
      );
    }

    throw new ServiceUnavailableException(
      `Scraper service communication failed: ${error.message}`,
    );
  }
}
