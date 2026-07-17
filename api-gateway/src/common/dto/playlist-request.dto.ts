import { IsUrl, IsNotEmpty, IsOptional } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class ImportPlaylistDto {
  @ApiProperty({
    description: 'The playlist URL to import',
    example: 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M',
  })
  @IsUrl({}, { message: 'Please provide a valid URL' })
  @IsNotEmpty({ message: 'URL must not be empty' })
  url!: string;
}

export class PlaylistQueryDto {
  @ApiPropertyOptional({
    description: 'The playlist URL to import',
    example: 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M',
  })
  @IsUrl({}, { message: 'Please provide a valid URL' })
  @IsOptional()
  url?: string;
}
