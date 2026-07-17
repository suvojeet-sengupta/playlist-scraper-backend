import { Injectable, Logger } from '@nestjs/common';
import { ScraperService } from '../scraper/scraper.service';
import {
  IPlaylistResponse,
  IPlatformsResponse,
} from '../../common/interfaces/playlist.interface';

@Injectable()
export class PlaylistService {
  private readonly logger = new Logger(PlaylistService.name);

  constructor(private readonly scraperService: ScraperService) {}

  /**
   * Import a playlist by URL.
   *
   * Delegates to the scraper microservice and returns the structured result.
   */
  async importPlaylist(url: string): Promise<IPlaylistResponse> {
    this.logger.log(`Importing playlist: ${url}`);

    // TODO: Implement caching layer (Redis / in-memory) to avoid
    //       re-scraping recently fetched playlists.
    //
    // const cached = await this.cacheService.get(url);
    // if (cached) {
    //   this.logger.log('Cache hit');
    //   return cached;
    // }

    const result = await this.scraperService.scrapePlaylist(url);

    // TODO: Cache the result with a TTL (e.g. 5 minutes).
    // await this.cacheService.set(url, result, 300);

    return result;
  }

  /**
   * List all supported platforms.
   */
  async getSupportedPlatforms(): Promise<IPlatformsResponse> {
    return this.scraperService.getSupportedPlatforms();
  }
}
