import {
  Controller,
  Post,
  Get,
  Body,
  Query,
  Logger,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiQuery,
} from '@nestjs/swagger';
import { PlaylistService } from './playlist.service';
import { ImportPlaylistDto } from '../../common/dto/playlist-request.dto';
import { UrlValidationPipe } from '../../common/pipes/url-validation.pipe';

@ApiTags('playlist')
@Controller('playlist')
export class PlaylistController {
  private readonly logger = new Logger(PlaylistController.name);

  constructor(private readonly playlistService: PlaylistService) {}

  /**
   * Import a playlist from a URL (POST body).
   */
  @Post('import')
  @ApiOperation({
    summary: 'Import a playlist',
    description:
      'Accepts a playlist URL in the request body, scrapes all track data, and returns structured JSON.',
  })
  @ApiResponse({ status: 200, description: 'Playlist scraped successfully' })
  @ApiResponse({ status: 400, description: 'Invalid or unsupported URL' })
  @ApiResponse({ status: 404, description: 'Playlist not found' })
  @ApiResponse({ status: 501, description: 'Platform not yet implemented' })
  @ApiResponse({ status: 503, description: 'Scraper service unavailable' })
  async importPlaylist(@Body() dto: ImportPlaylistDto) {
    this.logger.log(`POST /import – ${dto.url}`);
    return this.playlistService.importPlaylist(dto.url);
  }

  /**
   * Import a playlist from a URL (GET query param).
   */
  @Get('import')
  @ApiOperation({
    summary: 'Import a playlist via query parameter',
    description: 'Same as POST but the URL is passed as a query parameter.',
  })
  @ApiQuery({
    name: 'url',
    required: true,
    description: 'Playlist URL',
    example: 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M',
  })
  @ApiResponse({ status: 200, description: 'Playlist scraped successfully' })
  @ApiResponse({ status: 400, description: 'Invalid or unsupported URL' })
  async importPlaylistViaQuery(
    @Query('url', UrlValidationPipe) url: string,
  ) {
    this.logger.log(`GET /import – ${url}`);
    return this.playlistService.importPlaylist(url);
  }

  /**
   * List all supported platforms.
   */
  @Get('platforms')
  @ApiOperation({
    summary: 'List supported platforms',
    description:
      'Returns a list of all music platforms supported by the scraper, with status and URL patterns.',
  })
  @ApiResponse({ status: 200, description: 'Platforms listed' })
  async getSupportedPlatforms() {
    return this.playlistService.getSupportedPlatforms();
  }
}
