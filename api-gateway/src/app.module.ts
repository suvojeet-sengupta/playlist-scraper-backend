import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import configuration from './config/configuration';
import { PlaylistModule } from './modules/playlist/playlist.module';
import { ScraperModule } from './modules/scraper/scraper.module';
import { HealthModule } from './modules/health/health.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
    PlaylistModule,
    ScraperModule,
    HealthModule,
  ],
})
export class AppModule {}
