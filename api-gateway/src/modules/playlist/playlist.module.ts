import { Module } from '@nestjs/common';
import { ScraperModule } from '../scraper/scraper.module';
import { PlaylistService } from './playlist.service';
import { PlaylistController } from './playlist.controller';

@Module({
  imports: [ScraperModule],
  controllers: [PlaylistController],
  providers: [PlaylistService],
})
export class PlaylistModule {}
